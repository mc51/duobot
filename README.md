# Duobot is a complete and working command line automation for the Duolingo app

<p align="center">
  <img width="200" src="/assets/logo.webp">
</p>


# What is it?

Duobot is a complete and working command line automation for the Duolingo app written in Python. It travels the learning path of your currently active language course for you. Field by field it solves lessons, solves stories, and opens chests. Moreover, it collects XP and gems, improves your league position, contributes to daily quests and keeps your streak alive.

# Demo

https://github.com/user-attachments/assets/d3a4daf8-cc8d-4a94-992e-1ba53496eb81

# How to use it?

> [!WARNING]  
> This is an educational project. Use it at your own risk, as your Duolingo account might get banned.  
> Please don't abuse this in any way.  

First, clone the repo and `cd` into the folder. Then, create a virtual environment, activate it and install the package via pip:

```
python -m venv venv/
. venv/bin/activate
pip install .
```

Then, find your Duolingo app user id and a valid authorization token. Put them in a `.env` file in the root directory containing:

```
 DUO_USERID='123123'
 DUO_AUTH='Bearer eyF123123'
```

Finally, run Duobot with: `duobot --help` to see the options.

You can follow the progress Duobot makes by closing and opening the Duolingo app on your phone. It can take a few seconds for the path and all metrics to be updated.

# How does it work?

There's a [blog post](https://data-dive.com/duobot-automating-duolingo-by-reverse-engineering-android-app/) on this. In short:  
We reverse engineered the API of the official Duolingo Android app. To do so, we investigated how actions in the app are translated into API requests and responses. Finally, we automated all relevant requests to create a very close replicate of real user interactions with the app.  


# Why?

This is an educational project! Still, as of today, it's the only working Duolingo app automation on GitHub. In addition, it has the most advanced capabilities because it doesn't just do practice lessons but *all* lesson types.  
Obviously, you won't learn a language by letting the bot solve Duolingo challenges for you. But building this was a fun challenge in itself.
