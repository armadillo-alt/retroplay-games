/*
 * Stand-ins for thread calls the web runtime lacks. The page runs the emulator on one thread
 * (single-thread renderer, no CPU affinity), so these are never relied on.
 */
#include <errno.h>
#include <semaphore.h>
#include <stddef.h>
#include <time.h>

int pthread_getaffinity_np(void *thread, size_t size, void *set) { return ENOSYS; }
int pthread_setaffinity_np(void *thread, size_t size, const void *set) { return ENOSYS; }

int sem_timedwait(sem_t *sem, const struct timespec *abstime)
{
    if (sem_trywait(sem) == 0) return 0;
    errno = ETIMEDOUT;
    return -1;
}
