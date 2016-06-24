VK scripts
==========

A collection of scripts abusing VK.com API.

Prerequisites
-------------

Python 3.4 or higher is required.
Additionally, [online_duration.py] uses the excellent [matplotlib] plotting
library.
The versions the author is using are listed below.

Software     | Version
------------ | -------
Python       | 3.5.1
[matplotlib] | 1.5.1

[matplotlib]: http://matplotlib.org/

Usage
-----

The main package is located in the "vk/" directory.

Also, a few scripts are supplied in the "bin/" directory to showcase the
package's capabilities.
Run the scripts from the top-level directory using `python -m`.
Pass the `--help` flag to a script to see its detailed usage information.
The supplied scripts are listed below.

* [mutual_friends.py]: Learn who your ex and her new boyfriend are both friends
with.
* [track_status.py]: Track when people go online/offline.
* [online_duration.py]: View/visualize the amount of time people spend online.

[mutual_friends.py]: docs/mutual_friends.md
[track_status.py]: docs/track_status.md
[online_duration.py]: docs/online_duration.md

License
-------

This project, including all of the files and their contents, is licensed under
the terms of the MIT License.
See [LICENSE.txt] for details.

[LICENSE.txt]: LICENSE.txt
