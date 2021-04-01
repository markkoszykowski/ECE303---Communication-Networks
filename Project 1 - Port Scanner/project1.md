The first project is implementing a port scanner for a specific server/hostname.  Essentially you should be checking if a port is open on a specific server and if the port is a default port for a default service/application,  specify the application.  It should take arguments in the form of:
"./program hostname [-p 15:25]"
So the first argument is the hostname, and you guys can handle the option of inputting a port range.  If there isn't a range defined, scan ports from 1-1024.

Extra Details
Please only print ports that are active, dont print out ports that are not being used.
I know there are a ton of services, just support 15 common ones.  Also I understand another service may have the default port of something else open, dont worry about that.  Its ok that its a guess.
You cannot just import nmap or a similar library that does most of the project by itself!  I want you to write it yourself.  
For extra credit, you can also perform os fingerprinting (aka guessing what operating system the server is).  The attached paper talks about that a little.
If you have a program that takes arguments in a different way, please specify that in the submission.
If you have any classmates help, please specify/acknowledge that in your submission.    It's completely fine to get help within reason and I recommend it if you're struggling, but I want you to write and understand every line of the code you are submitting.  I highly recommend looking at stack overflow/etc as well.
If you are using anything besides python, c/c++, or golang , please verify with me if that language is ok to use.