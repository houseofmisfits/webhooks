# House of Misfits Webhook Repository

This is the Python script and the underlying rules files, that control all of the scheduled webhooks
for the Discord server House of Misfits.

## Quickstart / Links

If you want to see/control which messages go to which messages go which webhooks, and when, head over to 
the [schedules](schedules/) folder.

If you want to see/control what the messages actually say, go to the [rules](rules/) folder.

Edit these files and commit to new branches, then submit pull requests for those branches.

Messages are built using [Tracery](http://tracery.io) by GalaxyKate. Check out the 
[tutorial](http://www.crystalcodepalace.com/traceryTut.html) to learn more.

The Jenkins server (where the code runs) can be accessed at https://jenkins.misfits.house.

## How it works

### The Stack

The House of Misfits webhooks system runs on the following technologies:

 - GitHub (you are here! - stores the code)
 - Jenkins (downloads all the code from GitHub)
 - Docker (runs the code)
 - Python (the code)
 - Tracery (Python library that uses rules to generate sentences)
 - YAML (format the rules are written in)

Whenever a pull request (described below) is put into the `master` branch, GitHub notifies our Jenkins server that there
is new code to download. Once Jenkins is done downloading the code, it sends it to Docker, which 

### Schedules

The server uses all of the files in the `/schedules` folder to determine messages to send, where to send them, 
and when.

Note that it does not matter what file a schedule is in.

#### Syntax

The webhooks system expects each rule file to be in the following syntax:

```yaml
 - message: "#example_rule#" # origin of message to pick from rules
   webhook: webhook_name # defined in webhooks.yml
   schedule: 
     type: hourly # or other supported type
     # schedule syntax depends on type
   
```

#### Supported Types

The following types are currently supported:

 - **weekly**: sends a message at a specific time on a specific day of the week
```yaml
schedule:
  type: weekly
  days: # List of weekdays, i.e. Monday, Tuesday, etc.
    - Monday
    - Tuesday
  time: "14:00" # HH:MM in EST
```
 - **hourly**: sends a message every `interval` hours, starting from 00:00 EST
 ```yaml
schedule:
  type: hourly
  interval: 2 # or other integer
```
 
 - **minutely**: sends a message every `interval` minutes, starting from 00:00 EST
 ```yaml
schedule:
  type: minutely
  interval: 2 # or other integer
```

 - **random**: sends a message at random intervals, defined in `minutes_apart_range`
 ```yaml
schedule:
    type: random
    start_time: "06:00"  # HH:MM in EST 
    # This is the earliest a message can appear.
    end_time: "22:00"  # HH:MM in EST
    minutes_apart_range: 15-120
```
 
If another type is needed, [file an issue](https://github.com/houseofmisfits/webhooks/issues/new).



## Making changes

### Drafting Edits

With git, there are multiple ways you can edit files.

#### GitHub

You can edit files directly on the GitHub website. If you will occasionally make minor changes to rules and schedules,
this should suffice.

To edit a file, just click the filename to open it, and then click the pencil icon in the upper right-hand corner.

One important piece: **do *not* commit directly to the `master` branch**.

Instead, you will want to make a new branch, named something useful, and then commit to *that* branch.

Once you've made all of the changes you think you need, you can move on to submitting a Pull Request.

#### git clone

If you're more comfortable editing the files on your computer and can use your terminal/command prompt, that's also an
option.

You need to have GIT SCM installed (pre-installed on most non-Windows machines).

1. Download the repository; do `git clone https://github.com/houseofmisfits/webhooks.git`. 
  - Note: If you have two-step verification turned on, you will need to 
    [set up SSH](https://help.github.com/en/articles/adding-a-new-ssh-key-to-your-github-account) and clone with `git 
    clone git@github.com:houseofmisfits/webhooks.git` instead.
2. Go into the repository (`cd houseofmisfits`) and make a new branch to draft your changes onto (`git checkout -b 
my-super-cool-branch-name`).
3. Make your changes in a text editor of your choosing.
4. Once your done, "commit" your changes with `git add -A; git commit -m "Describe your changes here"`
5. Finally, send your changes back to GitHub with `git push -u origin my-super-cool-branch-name`

There are lots of tutorials online for git, so if you get stuck, you can check one of those.

Once you've pushed to your branch and you're satisfied with your changes, you can make a pull request.

#### PyCharm

If you will be changing the code or want to run the code to test rules, I recommend the PyCharm IDE. There
are, of course, other IDEs you can use, but I'm going to provide instructions on using PyCharm.

First, import a project from source control, and open `https://github.com/houseofmisfits/webhooks.git`
  - Note: If you have two-step verification turned on, you will need to 
    [set up SSH](https://help.github.com/en/articles/adding-a-new-ssh-key-to-your-github-account) and clone with `git 
    clone git@github.com:houseofmisfits/webhooks.git` instead.

When cloning the project, be sure to set up a virtual environment. The defaults *should* be okay, as long as you're
not using the main Python interpreter.

To create a new branch (i.e. a place to draft your changes), click `Git: master` on the bottom-right corner of the app
and select New Branch.... Name it something useful.

Then, you can make your edits in the IDE. Once you're done, commit the changes (one way to do this is the green check 
mark on the top-right corner of the IDE.)

Finally, push your changes (`VCS` > `Git` > `Push`). PyCharm will automatically set up a new remote for this branch and
push the code to GitHub on the new branch.

Once you've pushed to your branch and you're satisfied with your changes, you can make a pull request.

## Submitting Changes

In order for you to actually apply your changes to the server, you will need to create a Pull Request. (Note: This is a
GitHub specific thing, so it will need to be done from GitHub.com.)

While in your branch, you should see an icon next to the branch dropdown that says "New Pull Request". You can also go
to the "pull requests" tab and click "New Pull Request". Set your branch to go into Master, add some helpful comments,
and then submit.

Two things are required before you can merge your pull request:

 - Someone else must approve your changes
 - The automatic tests must pass (for example: if you forgot a colon `:` when defining a rule, it will fail.)
 
Once this is done, anyone can merge the pull request into master, and the changes will be applied as soon as the merge 
is complete.
