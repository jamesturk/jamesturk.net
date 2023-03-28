---
date: "2020-06-17"
title: "Postgres websearch in Django 3.1"
categories: [python, django]
---

Earlier this week, [Django 3.1 beta 1 was released](https://docs.djangoproject.com/en/dev/releases/3.1/).  While the big news is the addition of asynchronous views and middleware, there's a tiny feature I managed to [get added](https://github.com/django/django/pull/12215/commits/ff00a053478fee06bdfb4206c6d4e079e98640ff) that I wanted to bring a bit of attention to as it makes writing apps that use Postgres' full text search a little easier & nicer.

It's a [small line in the changelog](https://docs.djangoproject.com/en/dev/releases/3.1/#django-contrib-postgres), but the SearchQuery constructor now accepts the argument `search_type="websearch"`.  This allows you to write code like:

    Bill.objects.filter(
      search_vector=SearchQuery(
        "'transportation funding' OR 'transit funding' -highway",
        search_type="websearch",
        config="english"
      )
    )

Or take similarly human-formatted search queries from users and present results on your site with minimal fuss.  If you're already using Postgres &GreaterEqual; 11 this will be available to you as soon as you upgrade to Django 3.1, if you aren't familiar with Postgres' full text search it might be helpful to read on for a bit of background.

## Postgres Full Text Search

If you're using Postgres and haven't used its full text search functionality, you're likely missing out.  Whether your project is small and you think you can't afford the cost/time to add full text search, or your project is big and you think you need something much more powerful, it is worth at least looking at.

For example, [Open States](https://openstates.org) allows users to search across hundreds of thousands of pieces of state legislation.  We used to depend upon Elasticsearch, and so had additional servers, processes to keep data in sync between the two data stores, and a whole host of complex issues related to that setup.  In the past few months all of that has been replaced with a little bit of code that populates a tsquery field in Postgres, not only is the complexity much lower, the response time is much faster and the results are just as good.  (Elasticsearch is still a great product, but was overkill for our relatively straightforward needs.)

Without going into a full dissertation on how FTS works, it is useful to understand that Postgres' full text search works by converting text to a ``tsvector``, essentially a weighted list of keywords from a document.   When querying, the search query itself is converted to a ``tsquery``.

The example of doing this in SQL directly looks like this:

    SELECT to_tsvector('text goes here') @@ to_tsquery('text & here');

The argument to `to_tsquery` can use certain symbols like `&` and `*`, as well as ways to only search within certain parts of the tsvector.  (See [to_tsquery docs](https://www.postgresql.org/docs/12/textsearch-controls.html#TEXTSEARCH-PARSING-QUERIES).)

You'll notice that this syntax is pretty specific to `to_tsquery` and not how a user would typically assume a search field on a website would work.  We'll come back to that in a minute.

## Django & Postgres Full Text Search

Basic full text search support was added way back in Django 1.10.  The [Django Postgres Full Text Search Docs](https://docs.djangoproject.com/en/3.0/ref/contrib/postgres/search/) do a pretty good job, you'll see that it presents an interface that contains `SearchQuery` and `SearchVector` that can be used to interface with the underlying `tsquery` and `tsvector`.

If you want basic keyword search, or to handle custom search queries you craft in the ORM, that'll take you pretty far.

But if you take a look at the example on that page, you'll see that there's no difference in results between `SearchQuery('red tomato')` and `SearchQuery('tomato red')`.  Both evaluate to the same underlying `tsquery` object since  `to_tsquery` interprets spaces as an 'or'.  That's that same `tsquery` issue we flagged before.

So if you want to search for phrases you can craft your own miniature parser that handles words like 'and' & 'or', or takes care of quoted strings and uses the `search_type='phrase'` option available since Django 2.2.

Of course, any time you see the sentence "you can craft your own miniature parser" you probably start to sweat a little bit.  There are a lot of edge cases, and you're just trying to add search to your web application.

## Enter websearch_to_tsquery

As of Postgres 11, there is a new function available, `websearch_to_tsquery`. The docs sum it up well:

---

websearch_to_tsquery creates a tsquery value from query text using an alternative syntax in which simple unformatted text is a valid query. Unlike plainto_tsquery and phraseto_tsquery, it also recognizes certain operators. Moreover, this function should never raise syntax errors, which makes it possible to use raw user-supplied input for search. The following syntax is supported:

  * unquoted text: text not inside quote marks will be converted to terms separated by & operators, as if processed by plainto_tsquery.
  * "quoted text": text inside quote marks will be converted to terms separated by <-> operators, as if processed by phraseto_tsquery.
  * OR: logical or will be converted to the | operator.
  * -: the logical not operator, converted to the ! operator.

(via [Controlling Text Search, Postgres 11](https://www.postgresql.org/docs/11/textsearch-controls.html#TEXTSEARCH-PARSING-QUERIES))

---

Those rules are pretty useful, pretty much what most people would need if they were exposing search to their users.  This was essentially the missing feature from Postgres' search before Postgres 11.  Perhaps most important is the fact that it is safe to pass user input into this function, whereas passing it to `to_tsquery` and its cousins could often lead to a syntax error due to their peculiar syntax and rigid parsing.

This means we can write searches like `"ham sandwich" OR "turkey sandwich" -mustard` in a search box on our site, and pass it through to Postgres and have it just work!

So that's where that line of Django code from the beginning of this article comes in.  By passing `search_type="websearch"` to SearchQuery, you can use this powerful Postgres feature.  This will be available on Django &GreaterEqual; 3.1 and only if you're on Postgres &GreaterEqual; 11.
