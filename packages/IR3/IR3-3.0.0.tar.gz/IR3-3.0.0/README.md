# IR3 - The IR-3 project!

With Scrapeasy, you can find the activity value and designing enzyme for input substrate.

## Usage

In the following paragraphs, I am going to describe how you can get and use IR3 for your own projects.

###  Getting it

To download IR3, either fork this github repo or simply use Pypi via pip.
```sh
$ pip install IR3
```

Additionally, make sure to download the mutation_table.csv file provided in this repository and place it in the same location as your code. This file is necessary for the proper functioning of IR3.

### Using it

IR3 was programmed with ease-of-use in mind. First, import process_substrate from IR3

```Python
from IR3 import process_substrate
```

And you are ready to go! At this point, I want to find the activity value and designing enzyme for a substrate path as "input_sequence.txt"

## Default Output Path

If you prefer to save the output.txt file in the current directory, simply use:

```Python
process_substrate('input_sequence.txt')
```

## Custom Output Path

If you want to specify a custom path for the output.txt file, you can do so by providing the desired file path:

```Python
process_substrate('input_sequence.txt', output_path='your_specific_folder_path/output.txt')


License
----

MIT License

Copyright (c) 2024 Xinxin Yu

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

