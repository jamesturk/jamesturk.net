+++
date = "2023-03-16T12:00:00-05:00"
draft = false
title = "Automated Scraping with GPT-4"
+++


Like most people I know, I've been watching the pace of improvements to LLMs like ChatGPT and GPT-4 with a mix of awe and trepidation. I've been wanting a small project to get to explore the APIs better, and recently decided I'd try to see if I could use it to automate web scraping.

For context, I've written a lot of web scrapers. For the better part of thirteen years, I ran [Open States](https://openstates.org), a project that scraped state legislative websites to make them more accessible to the public. The biggest challenge in running a project like that is keeping up with the constant changes to the websites you're scraping.

Writing web scrapers is a translation task, you take a piece of HTML and transform it to a structured data format. From what I understand, LLMs should be good at this task. They also seem to parse HTML and JSON well enough that existing models should be useful to generate a scraper.

In practice this looks something like this:

```python
import openai

html = requests.get(url)
completion = openai.ChatCompletion.create(
    engine="gpt-4",
    # this controls how long the JSON output can be, 
    # 2048 tokens is about 8,000 characters
    # which should be more than enough 
    # (note: this impacts the cost of the request)
    max_tokens=2048,
    # temperature controls how random the output is
    # 0 is completely deterministic
    # which is what we want for scraping
    temperature=0,
    # at the time of writing I only had GPT-4 
    # access via the chat interface
    messages=[
        {
            "text": 'Convert the given HTML to JSON with the schema' 
            '{"name": "string", "age": "number"}',
            "user": "system",
        },
        {
            "text": html.text,
            "user": "user",
        },
    ],
)
# extract JSON 
data = json.loads(completion.choices[0]["message"]["content"])
```

I first decided to try it against Illinois state legislators.

I gave it a schema of:

```python
    schema={
        "name": "string",
        "url": "url",
        "district": "string",
        "party": "string",
    }
```

and it was able to extract information from pages like <https://www.ilga.gov/senate/Senator.asp?GA=103&MemberID=3092>

And if you change the schema to include some nested fields:

```python
    schema={
        "name": "string",
        "url": "url",
        "district": "string",
        "party": "string",
        "offices": [{
            "name": "string",
            "address": "string",
            "phone": "string"
        }],
    }
```

It handles the change perfectly.

## Is It Actually Good?

Anecdotally, yes.

I've run it against some Open States scrapers and it performs very well. Testing gets a bit expensive so I haven't run it against a comprehensive test suite, but I'm impressed so far with what I've tried.

I'll probably give it a more thorough test in the future once I experiment more with cost-saving techniques like cleaning the HTML more before sending it.

## Is It Practical?

I didn't think the answer would be yes when I started, but... definitely more than I thought.

As I write this, GPT-4 is in preview and there's only one API method available, not the full range of options.  This makes it more expensive.  It can cost up to $0.36/request right now depending on the specifics of the request.

For a one-off scrape that won't need that many requests, that might not be terrible compared to the time you'd spend building it.

(A note on pricing: Long term it will likely be more reasonable to use the InstructGPT interface, which ranges from $0.02 to $0.0004 per 1000 tokens. If prior trends are any indication, the $0.02 model will soon be a GPT-4 model.  Pricing will definitely come down as the model matures.)

For scrapes that are running regularly, a different approach might make more sense depending on the frequency it'll run and other factors.

Beyond cost, the other big limitation is the token limit. GPT-3.5's 4096 tokens is not a lot of HTML and I frequently ran into issues with it.  GPT-4 has a 8192 token limit, which is much better and allowed me to complete the scraper for the Illinois legislators without any tricks.

It's worth noting, longer pages (such as the full list of legislators) are too big.
There is an announced-but-currently-unavailable 32k token limit version of GPT-4, which would be ideal for larger pages, once I have access to that I'll be revisiting this with some other ideas I want to try.

## scrapeghost

If this is interesting to you, I decided to take what I had above and make it into a little proof-of-concept module that can be used to actually scrape sites.

If you have your own OpenAI API key, you can play with what I have working here: <https://github.com/jamesturk/scrapeghost/>

Though it isn't much, I figured I'd share what I've learned so far and I figure others might have ideas on how to improve this approach.

Using it looks like:

```python
>>> from scrapeghost import SchemaScraper
>>> scrape_legislators = SchemaScraper(
    schema={
        "name": "string",
        "url": "url",
        "district": "string",
        "party": "string",
        "photo_url": "url",
        "offices": [{
            "name": "string", 
            "address": "string",
            "phone": "string"}],
    }
)
>>> scrape_legislators(
    "https://www.ilga.gov/house/rep.asp?MemberID=3071"
)
{'name': 'Emanuel "Chris" Welch',
 'url': 'https://www.ilga.gov/house/Rep.asp?MemberID=3071',
 'district': '7th', 'party': 'D', 
 'photo_url': 
 'https://www.ilga.gov/images/members/{5D419B94-66B4-4F3B-86F1-BFF37B3FA55C}.jpg',
  'offices': [
    {'name': 'Springfield Office',
     'address': '300 Capitol Building, Springfield, IL 62706', 
     'phone': '(217) 782-5350'},
    {'name': 'District Office', 
    'address': '10055 W. Roosevelt Rd., Suite E, Westchester, IL 60154',
     'phone': '(708) 450-1000'}
   ]}
```

v0.1 isn't even 100 lines of code, just the above with some quality-of-life features.  Feel free to open an issue on GitHub if you have any ideas for improvements.

One that can matter a great deal if you're actually going to use this is to reduce how much HTML you send by using the `xpath_hint` or `css_hint` parameters. These add a preprocessing step that uses the given selector to reduce the HTML sent to the API.  Since you're paying per token, this can be a big deal, or even make scraping a large page possible where it would otherwise exceed the token limit.

## Other Ideas

### What about not calling the API every time?

I'm interested in playing with this, but it might be a different thing.

The most obvious improvement might be to instead have the scraper generate a translation function of its own so that it isn't necessary to send every request to the API.

Generating the XPath/CSS selectors is possible but from my limited testing, seemed less reliable.

It is also worth noting, the current approach should lead to the most robust scrapers, since if each page differs each time it is scraped, the scraper should still perform well.

It also isn't as simple as just modifying the prompt, an approach with intermediate output will be necessary.

With a single example page it would be impossible to get it to write robust XPath, so if there is any variance in the pages being scraped it is likely to fail.  Providing multiple pages would stress even the 32k token limit. This means such a usage would require using the [fine-tuning](https://platform.openai.com/docs/guides/fine-tuning) features of the API.

The other big challenge will be that to grab nested data like the addresses in the above example, you often need some logic outside XPath. You can't just map each key to a single XPath.

It'd therefore be necessary to have the scraper generate some intermediate output that could be used to automate the scraping.  (One option would be to ask it to write Python, another would be to provide it some sort of simplified DSL to write the scraper in.)

### Why didn't you use XYZ instead?

I'm sure there are other tools that could be used to do this.  I'd love to hear about them, but this was just a quick experiment with OpenAI's API.

### What about pages where the data isn't in the HTML?

Depending on the way the data is on the page (e.g. some state sites have a JSON array with all legislators in them) some might just work, but pages with external requests or other dynamic content will need a different approach.

### What about pages with a lot of data?

If the hint approach is not good enough, the 32k token limit should be enough to scrape a lot of data once it is available.
