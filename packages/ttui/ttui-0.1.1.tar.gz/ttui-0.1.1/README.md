# TTUI
___
A terminal application to view .txt files quickly. Built for my personal use.

## Why
___

I was sick of reading information in txt files and did not want to create a method to read them. Here is my solution an application that will open a terminal application showing the data in a table.

Ever dump python dicts into a txt file? Well I do and I do it a lot for random scripts, projects, or when I need to cache data. TTui will parse the index of the string given a type of object and return each line in the .txt as the object.

Also, I wanted to figure out how to publish to pypi which was important to me.

___
## How?
___

Ideally, install pipx is the easiest.

```
pipx install ttui
```

Once installed the ```tt``` command will be added to your path.

It's meant to just take the argument of the file path.

```
tt demo.txt
```

Don't try to pass an empty file to the program, it will just return a warning and nothing will happen.

## Development
___

Going to...
- More types ie tuples, list, and custom types
- Clean the code base
- a way to filter data