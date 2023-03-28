---
date: "2023-03-18"
title: "Automated Scraping with GPT, Part 2"
categories: [python, gpt]
---

![A scrapeghost, appropriately drawn by DALL-E](dall-e-scrapeghost.png)

A couple of days ago I wrote about [using GPT-4 to automate web scraping](/posts/scraping-with-gpt-4/). I was surprised at how well it worked for a first attempt and have been curious how far I go to make it useful.

I'm building an experimental interface here if you'd like to follow along: <https://github.com/jamesturk/scrapeghost>

Here's what I've been working on:

## Command Line Interface

If you'd like to just quickly experiment with the tool, I've added a command line interface.

If you install it with `pipx install scrapeghost` you can then run it like this:

```bash
$ scrapeghost https://www.ncleg.gov/Members/Biography/S/436  \
  --schema "{'first_name': 'str', 'last_name': 'str',
             'photo_url': 'url', 'offices': [] }"  \
  --gpt4 

{'first_name': 'Gale',
 'last_name': 'Adcock',
 'photo_url': 'https://www.ncleg.gov/Members/MemberImage/S/436/Low',
 'offices': [
    {'address': '16 West Jones Street, Rm. 1104',
     'city': 'Raleigh', 'state': 'NC', 'zip': '27601',
     'phone': '(919) 715-3036',
     'email': 'Gale.Adcock@ncleg.gov',
     'legislative_assistant': 'Elizabeth Sharpe',
     'legislative_assistant_email': 'Elizabeth.Sharpe@ncleg.gov'
    }
  ]
}
```

That's all it takes, you define a rough schema and it will try to extract data from the page to match it.

The more specific your schema is, the better the results will be.

## Token Minimization

As I noted in the original post, to make this remotely practical, reducing the number of tokens is key.

Fewer tokens means cheaper & faster requests.  It also means more pages that can be scraped since even GPT-4 has a token limit easily exceeded by a single page of HTML.

I've implemented three approaches to working with the token limit:

* **Automatic cleaning of the HTML.**  Using `lxml.html.clean`, many pages can be reduced in size by about 1/3, things like script tags, styles, and comments are removed. This was a simple change I took too long to make.
* **Allow using a CSS/XPath selector to extract relevant portion(s) of the page.**  This requires a little bit of manual work to figure out the right selector, but it can be a huge win.
* **Optional page-splitting.**  For list-type pages, allow for the page to be broken up into multiple API calls. This is the most complicated and prone to failure, but on the right kind of page can effectively remove the token limit.  (Also this can be quite costly, but the option now exists.)

With this I've been able to scrape a broader variety of pages.  See the [examples](https://github.com/jamesturk/scrapeghost/tree/main/examples) directory for some examples.

## GPT 3.5 / GPT 4

It is now possible to use GPT-3.5-turbo instead of GPT-4 - [Simon Willison](https://fedi.simonwillison.net/@simon) pointed out how much cheaper GPT-3.5-turbo is, and I'd only played with it a little bit but discarded it due to the token limit. Now that I have multiple ways to work with the token limit, it is a lot more practical to use.

The good news is that for most of the examples I've tried, GPT-3.5-turbo performs just as well at a fraction of the price.

It also means anyone with an OpenAI API key can play with the tool since not all accounts have GPT-4 access yet.

The default behavior is to try GPT-3.5-turbo first, and then fall back to 4 if there's an invalid response or the request was too large. This can be a great cost-saving option if most of your requests work on 3.5 but a few fail/need a larger token limit.

Relatedly, I've made the prompt a little bit more detailed to try to get better results. GPT-3.5 seems to produce invalid JSON a little bit more often than GPT-4 had been, so I've added some additional commands to help remedy that. I'm not sure how much they're helping at the moment but they fixed a couple of test cases I had.

## Experiments

I've added an experimental class that can follow pagination links, and it seems to work well on a few test cases. I'm hoping to broaden the types of pages it works with soon.

I'm planning to work on a few more experiments & improvements soon:

* **Automatic JSON repair** - A couple of people pointed out I could probably ask GPT to repair its own invalid JSON. This is a fun idea & I need to give it a try.
* **Cost-related features** - With the pagination and chunking features, it's possible to have a single call make a lot of requests.  I'm tracking tokens now & so it should be possible to set maximum costs for a request, and also to track the cost of a session.
* **Hybrid-mode** - In the first post, I explained why I'm not asking it to generate CSS/XPath selectors. I realized while working on the chunking-mode that there's a way to combine the two approaches for large pages, I need to give it a try.
* **Use tokenization library** - Right now I'm just estimating the token length based on string length, but I should bring in the actual token counting tools OpenAI provides.

Let me know if there are other ideas you'd like to see, glad to take suggestions!
