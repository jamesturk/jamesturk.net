---
date: "2023-01-07"
title: "Moving from (n)vim to VS Code in 2023"
---

I've been a vim user for more than 15 years. Before then I would try a new editor every few months, Visual Studio, Komodo IDE, Kate, and JEdit are a few that I remember sticking with for a while before hitting some wall and looking elsewhere. So when I eventually took the time to learn vim and found that I really enjoyed working in it, I figured I was done switching editors.

Eventually `tmux` became part of my workflow too, and I was shockingly productive with the pairing. I didn't really think much about it anymore, my `.vimrc` hadn't changed much in the last five years beyond the migration to a `.nvim/init.vim`. I certainly wasn't a power user/evangelist or anything, if anything I was a bit embarassed at how bad I appeared to be at typing if I had to use a colleague's machine for a minute. A trail of random vim keystrokes almost compulsively typed into their SublimeText, Atom, or for the past few years, VS Code.

Of course, I'd installed most of these editors, tried their vim-mode & given up before doing any real editing in them. Even if I could make them on par with my current setup, why spend the time?

## Enter VS Code

This fall I started teaching, and my students mostly use VS Code.

They're of course free to use whatever, but VS Code pretty quickly became the default for new developers. My students were no exception, the department provides a lot of support & documentation for those that wish to use VS Code.

Up until last fall however, I hadn't really used it. I knew that the language-server stuff that has made its way to neovim had origiated in VS Code, and from what I understood of them it was a neat innovation. I'd even set up `neovim` to use some, but hadn't really taken full advantage.

I felt a little silly the first time one of my students asked me to remind them how to open a terminal within VS Code and I wasn't sure.
While there's nothing wrong with encouraging a student to learn their own tools, I felt like it'd be nice if I could answer basic questions like that instead of having to stop what we were doing and wait for them to look it up.
I am a firm believer that taking the extra time to get to know your tools can really improve your life as a developer and wanted to be able to demonstrate that to them.
I wasn't going to encourage them to install the same vim plugins as me, so it'd be nice to have some suggestions for how to make their lives easier in a tool they were actually going to use.

## False Starts

I'd tried VS Code once before, when I was working on a project that had some TypeScript in it.

Here's how I remember it from that trial run:

- I'd installed it to work in JavaScript, a language I prefer not to write. I appreciated that it had a lot of plugins that made life easier and I didn't have to spend too much time configuring them to get things into a good enough state.  I didn't have a ton of JS plugins in my `vim` config, so I wasn't looking for much, and what I got exceeded expecations.
- It had a good enough `vim` mode I could type without tripping over myself, but I didn't really get into it beyond that. If anything, using it just to write JavaScript made me develop a negative association with that window.
- I remembered hating something about the default theme, which is fairly petty I realize. Plus I don't even remember what it was.
- I also hated the symbols on the left sidebar, I could never remember what they were and there were way too many of them.

So yeah, maybe not an entirely fair chance.

## Committing for a month

I decided it made sense to use VS Code for a month, that'd at least force me to learn the basics. I'd be able to open a terminal for sure, and probably develop some preferences on useful plugins and such that I could share with beginner students when asked.

The first thing I noticed was that it was *actually fast*. I jump around quickly with vim keybindings, and VS Code never once during the trial period felt sluggish the ways other editors had compared to vim. That would usually be the thing that'd send me back.

Second, it was well-configured out of the box. Plugin recommendations were a click away and I didn't initially need to sink a ton of time to get a very functional experience.

I just didn't want to spend a week setting it up, I knew from experience I'd go on a yak-shaving expedition and had a lot of work to do.
I landed on an approach that worked really well.
I created small file (in `vim`, as was my habit), a "vscode.md" where I kept a sort of list of pain points. If I found myself hating that theme again, I'd add a bullet for "find more distinct color theme" and keep working.
Then whenever I had a bit of downtime and felt like tinkering, I'd knock a few issues off my list.

This had the effect of keeping me really productive in VS Code, which meant I was using it more and more, which meant I was finding more things to tweak, and pretty quickly I had a configuration that was amazingly ergonomic.

I also found myself really enjoying the language server experience. I'm sure there are ways to get more out of it in neovim but I hadn't gone beyond the basics. Right out of the gate I had autoformatting via `black`, `pytest` integration, an easy to use visual debugger, and a half a dozen other things that make writing Python much more pleasant.

Another thing I hadn't anticipated appreciating was having support for things like HTML and PDFs (via a plugin) side-by-side with my editor.  When I'm on my Macbook, the main thing I miss about running Linux as my daily driver is using a tiling window manager.  Between that and `tmux`, the more content I can get into split panes the happier I am.  Being able to watch a page or PDF live-reload while I edited HTML or LaTeX within the editor felt like I'd regained something I'd given up.

I don't think it makes a ton of sense to go into all the specifics of my setup as everyone has their own needs & way of working and mine are about as idiosyncratic as anyone's, but here is a quick list of some things I found that I like:

- Some of the obvious ones like Pylance, GitHub, Vim, etc.  I'm impressed with how well they all work and how little configuration it took.
- [Code Spell Checker](https://marketplace.visualstudio.com/items?itemName=streetsidesoftware.code-spell-checker) - Code spell check was always annoying to me in vim, but finding this one quite useful.
- [just](https://marketplace.visualstudio.com/items?itemName=kokakiwi.vscode-just) - Justfile support.
- [Peacock](https://marketplace.visualstudio.com/items?itemName=johnpapa.vscode-peacock) - I love this one, different color per window is really nice. Config is stored in the repo and it switches instantaneously so I can have a color differ based on a git branch.
- [Todo Tree](https://marketplace.visualstudio.com/items?itemName=Gruntfuggly.todo-tree) - A nice tree of all TODO comments in your files.

I haven't even tried using the `neovim` integration.  That felt like cheating for this experiment, but I'm excited to give it a go.

I will note, the biggest item left in my `vscode.md` wishlist is better support for `poetry`. In particular I wish it'd automatically use poetry's virtualenv if it finds a `pyproject.yaml` with `poetry` configured. I assume that'll happen sooner or later.

### Aside: GitHub Copilot

I'd steered clear of [Copilot](https://github.com/features/copilot) at launch due to the copyright issues & controversy.
Since it was right there a click away, I was curious during this trial period and enabled it and was incredibly surprised by it.
While a completely separate topic, I found it to be very useful in generating examples and tests based on a comment.  I loved this for things like writing out example API output and simple unit tests. It both excels at these tasks and when used this way ran no real risk of violating anyone's copyright.
I also found it useful with the option to use public code turned off, I found it worked just as well for my use cases and provided some extra piece of mind.

There's a whole lot more to be said about Copilot, in terms of unintended plagiarism, copyright, and the troubling mistakes it can make when outside of its "comfort zone."
That said, now that it is here, I am pretty sure I'll continue to use it when experimenting with new APIs, drafting outlines, and writing tedious code like test fixtures.

### Moving Forward w/ VS Code

While I still find myself opening `vim` for quick scripts, that's partially out of habit.

I've already found myself missing a VS Code luxury once a "quick script" grows beyond my initial plans for it & switching over to VS Code.

I still have a ways to go in terms of adding more shortcuts & developing muscle memory, and I'd really like to get those last few pain points in vim-mode figured out, I don't see why I'd switch back for day-to-day development.

I look forward to giving the debugger a more thorough workout when I have something more serious to use it for.

And ultimately, it has been nice having some experience in a tool so widely used by my students. When I see them struggling with something I have more of an idea of how to make a helpful suggestion, whether it is a setting, shortcut, or plugin.

The fact that I enjoy using it was an extremely pleasant surprise.
