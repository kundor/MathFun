/* https://math.stackexchange.com/questions/3308163/generalization-on-a-feature-of-21 */

#include "include/mp.h"
#include "include/msieve.h"
#include "include/common.h"

#define MAXPOW 100
#define MAXN 100000
/* bigger would exceed 300 digits, which is the largest msieve can handle */

void get_random_seeds(uint32 *seed1, uint32 *seed2) {

	uint32 tmp_seed1, tmp_seed2;

	/* In a multithreaded program, every msieve object
	   should have two unique, non-correlated seeds
	   chosen for it */

#if !defined(WIN32) && !defined(_WIN64)

	FILE *rand_device = fopen("/dev/urandom", "r");

	if (rand_device != NULL) {

		/* Yay! Cryptographic-quality nondeterministic randomness! */

		fread(&tmp_seed1, sizeof(uint32), (size_t)1, rand_device);
		fread(&tmp_seed2, sizeof(uint32), (size_t)1, rand_device);
		fclose(rand_device);
	}
	else

#endif
	{
		/* <Shrug> For everyone else, sample the current time,
		   the high-res timer (hopefully not correlated to the
		   current time), and the process ID. Multithreaded
		   applications should fold in the thread ID too */

		uint64 high_res_time = read_clock();
		tmp_seed1 = ((uint32)(high_res_time >> 32) ^
			     (uint32)time(NULL)) * 
			    (uint32)getpid();
		tmp_seed2 = (uint32)high_res_time;
	}

	/* The final seeds are the result of a multiplicative
	   hash of the initial seeds */

	(*seed1) = tmp_seed1 * ((uint32)40499 * 65543);
	(*seed2) = tmp_seed2 * ((uint32)40499 * 65543);
}

msieve_obj * get_mobj() {
	msieve_obj *obj = (msieve_obj *)xcalloc((size_t)1, sizeof(msieve_obj));

	obj->input = NULL;
	obj->flags = MSIEVE_DEFAULT_FLAGS;
    get_random_seeds(&(obj->seed1), &(obj->seed2));
	obj->max_relations = 0;
	obj->cpu = get_cpu_type();
    get_cache_sizes(&(obj->cache_size1), &(obj->cache_size2));
	obj->num_threads = 0;
	obj->which_gpu = 0;
	obj->logfile_name = MSIEVE_DEFAULT_LOGFILE;
	obj->nfs_args = NULL;
	obj->nfs_fbfile_name = MSIEVE_DEFAULT_NFS_FBFILE;
	obj->mp_sprintf_buf = (char *)xmalloc(32 * MAX_MP_WORDS + 1);
    savefile_init(&obj->savefile, MSIEVE_DEFAULT_SAVEFILE);
	
	return obj;
}

void add_factors(const mp_t *n, factor_list_t *list, mp_t* sum);

uint32 msieve_run_core(msieve_obj *obj, mp_t *n, factor_list_t *factor_list);

void mrun(const mp_t* n, msieve_obj* obj, mp_t* sopfr) {
	int32 status;
	uint32 i;
	mp_t reduced_n;
	factor_list_t factor_list;

	factor_list_init(&factor_list);

	/* perform trial division */

	trial_factor(obj, n, &reduced_n, &factor_list);
	if (mp_is_one(&reduced_n))
		goto clean_up;

	/* save the remaining cofactor of n; if composite,
	   run Pollard Rho unconditionally */

       	if (factor_list_add(obj, &factor_list, &reduced_n) > 0)
		rho(obj, &reduced_n, &reduced_n, &factor_list);

	/* if still composite, and not quite small, 
	   run P+-1 and ECM. These could take quite a while
	   to run, so allow interruptions to exit gracefully */

       	if (factor_list_max_composite(&factor_list) > 
				SMALL_COMPOSITE_CUTOFF_BITS) {

		obj->flags |= MSIEVE_FLAG_SIEVING_IN_PROGRESS;
		ecm_pp1_pm1(obj, &reduced_n, &reduced_n, &factor_list);
		obj->flags &= ~MSIEVE_FLAG_SIEVING_IN_PROGRESS;
		if (obj->flags & MSIEVE_FLAG_STOP_SIEVING)
			goto clean_up;
	}

	/* while forward progress is still being made */

	while (1) {
		uint32 num_factors = factor_list.num_factors;
		status = 0;

		/* process the next composite factor of n. Only
		   attempt one factorization at a time, since 
		   the underlying list of factors could change */

		for (i = 0; i < num_factors; i++) {
			final_factor_t *f = factor_list.final_factors[i];

			if (f->type == MSIEVE_COMPOSITE) {
				mp_t new_n;
				mp_copy(&f->factor, &new_n);
				status = msieve_run_core(obj, &new_n,
							&factor_list);
				break;
			}
		}
		if (status == 0 || (obj->flags & MSIEVE_FLAG_STOP_SIEVING))
			break;
	}

clean_up:
	add_factors(n, &factor_list, sopfr);
}

void add_factors(const mp_t *n, factor_list_t *list, mp_t* sum) {
    uint32 i;
    mp_t q, r, tmp;
    mp_clear(sum);

    /* if there's only one factor and it's listed as composite,
       don't save anything (it would just confuse people) */

    if (list->num_factors == 1 && 
        list->final_factors[0]->type == MSIEVE_COMPOSITE) {
        free(list->final_factors[0]);
        return;
    }   

    /* report each factor every time it appears in n */

    mp_copy(n, &tmp);
    for (i = 0; i < list->num_factors; i++) {
        final_factor_t *curr_factor = list->final_factors[i];

        while (1) {
            mp_divrem(&tmp, &curr_factor->factor, &q, &r);
            if (mp_is_zero(&q) || !mp_is_zero(&r))
                break;

            mp_copy(&q, &tmp);
            mp_add(sum, &curr_factor->factor, sum);
        }

        free(curr_factor);
    }
    return;
}


int main() {
    mp_t sumps[MAXPOW]; /* sum of kth powers; sumps[0] is 1 + 2 + ... + n,
                       * sumps[2] is 1 + 4 + ... + n^2,
                       * sumps[99] is 1 + 2^99 + ... + n^99 */
    mp_t curnp, sopfr;
    msieve_obj* obj = get_mobj();
    for (int i=0; i < MAXPOW; ++i) {
        mp_clear(&sumps[i]);
        mp_add_1(&sumps[i], 1u, &sumps[i]);
    }
    for (uint32 n = 2; n < MAXN; ++n) {
        mp_clear(&curnp);
        mp_add_1(&curnp, 1u, &curnp);
        for (int pow = 0; pow < MAXPOW; ++pow) {
            obj->flags = MSIEVE_DEFAULT_FLAGS;
            mp_mul_1(&curnp, n, &curnp);
            mp_add(&sumps[pow], &curnp, &sumps[pow]);
            mrun(&sumps[pow], obj, &sopfr);
            if (sopfr.nwords == 1 && sopfr.val[0] == n) {
                printf("g(f(%u,%d)) = %u\n", n, pow+1, n);
            }
/*            else {
                printf("g(f(%u,%d)) =", n, pow+1);
                mp_print(&sopfr, 10, stdout, obj->mp_sprintf_buf);
                printf("\n");
            } */
        }
    }

    return 0;
}
