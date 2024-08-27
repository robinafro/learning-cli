# learning-cli
a cli tool for studying

This CLI app written in Python makes it very easy to memorize answers to questions. Primarily intended for studying for exams where you need to quickly learn a bunch of stuff.
![image](https://github.com/user-attachments/assets/c810e117-a6cc-416f-8961-647dee6489cf)

## usage
You can create courses, which are simply collections of questions using the `new` command, like this:
![image](https://github.com/user-attachments/assets/b42b9379-5ac1-4bdc-af54-b29defaf3533)

Then, you can use the `start` command to run the course and start answering the questions!
![image](https://github.com/user-attachments/assets/8020fbcc-d53e-43a0-99ce-e296e9e2db05)
*tip: you don't have to copy the entire ID, just type a part of it!*

It uses difflib's **SequenceMatcher** to find the similarity of your answer to the correct one. It's not always perfect, but it's way better than just comparing the strings directly.

Another very important feature is *importing courses*. Since this app is intended to be used to quickly learn something, I assume you don't have the time to write all the questions yourself. That's when ChatGPT comes into play!
![image](https://github.com/user-attachments/assets/be2bec00-0970-4c95-b7bb-43a39413d37f)

Just ask ChatGPT to generate the questions and answers, then import them using the `import` command:
![image](https://github.com/user-attachments/assets/f7fd1b40-3f0d-4844-aa72-6c5a91e2b4a1)

And paste it in!

![image](https://github.com/user-attachments/assets/eb8a88bd-22a4-4eeb-8341-bb02524272ab)
*tip: I recommend to first reduce the JSON to one line, because terminals / python usually don't handle newlines correctly.*

There are many more commands, such as deleting or appending questions to an existing course. You can view those using the `-h` flag or by running the script with no commands.

### Happy studying!

---

## the future
In the future, I plan on adding a lot more features, such as graphing your progress (past scores on one course), an algorithm that prioritizes questions that you struggle with and more!
If you're interested in helping out with this, feel absolutely free to open a pull request! :)
