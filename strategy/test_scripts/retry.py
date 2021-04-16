import time
from functools import partial, wraps
import logging
from sys import exit

# this is referring the main script logger
logger = logging.getLogger('__main__')


def retry(func=None, exception=Exception, n_tries=5, delay=5, backoff=1, tolog=True, kill=False):
    # logger.info('Retry function from another file')
    """Retry decorator with exponential backoff.

    Parameters
    ----------
    func : typing.Callable, optional
        Callable on which the decorator is applied, by default None
    exception : Exception or tuple of Exceptions, optional
        Exception(s) that invoke retry, by default Exception
    n_tries : int, optional
        Number of tries before giving up, by default 5
    delay : int, optional
        Initial delay between retries in seconds, by default 5
    backoff : int, optional
        Backoff multiplier e.g. value of 2 will double the delay, by default 1
    tolog : bool, optional
        Option to log or print, by default True
    kill : bool, optional
        Option to kill the execution of the sript, by default False

    Returns
    -------
    typing.Callable
        Decorated callable that calls itself when exception(s) occur.

    Examples
    --------
    >>> import random
    >>> @retry(exception=Exception, n_tries=4)
    ... def test_random(text):
    ...    x = random.random()
    ...    if x < 0.5:
    ...        raise Exception("Fail")
    ...    else:
    ...        print("Success: ", text)
    >>> test_random("It works!")
    """

    if func is None:
        return partial(retry, exception=exception,
                       n_tries=n_tries, delay=delay,
                       backoff=backoff, tolog=logger, kill=kill,)

    @wraps(func)
    def wrapper(*args, **kwargs):
        ntries, ndelay, nkill = n_tries, delay, kill

        while ntries >= 1:
            try:
                return func(*args, **kwargs)
            except exception as e:
                msg = f"Exception in {func.__name__} ==> {str(e)}, Retrying in {ndelay} seconds..."
                if tolog:
                    logger.warning(msg)
                else:
                    print(msg)
                time.sleep(ndelay)
                ntries -= 1
                ndelay *= backoff
                if nkill and ntries == 0:
                    logger.info(f'{func.__name__} ==> failed all the retires.. Exiting.')
                    exit()

        return func(*args, **kwargs)

    return wrapper

