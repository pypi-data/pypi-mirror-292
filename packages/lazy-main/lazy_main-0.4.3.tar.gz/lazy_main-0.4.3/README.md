# lazy-main
Generalized framework for main loop function.

## Installation
```sh
pip install lazy-main
```

## How to Use
```py
from lazy_main import LazyMain

def main(*args, **kwargs):
    print("Hello World!")

def error_handler(exception):
    print("An error occurred!", exception)

if __name__ == "__main__":
    LazyMain(
        main=main,
        error_handler=error_handler, # This is optional.
        sleep_min=3,
        sleep_max=5,
        print_logs=True,
        loop_count=-1, # -1 Means it will loop infinitely.
    ).run()
```

You can also pass arguments to the `main` function.

```py
from lazy_main import LazyMain

def main(*args, **kwargs):
    print(kwargs["hello"]) # World!

if __name__ == "__main__":
    LazyMain(
        main=main,
    ).run(
        hello="World!",
    )
```

Returning `True` will print the total elapsed time.

```py
from lazy_main import LazyMain

def main():
    return True

if __name__ == "__main__":
    LazyMain(
        main=main,
    ).run() # Done in 0.10s.
```

Returning `SIGTERM` will terminate the loop.

```py
from lazy_main import LazyMain
import signal

def main():
    return signal.SIGTERM

if __name__ == "__main__":
    LazyMain(
        main=main,
    ).run()

    print("I'm free!")
```