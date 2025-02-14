Schedule and deploy:

- I would schedule a cron-jobs running every night to query the data (that is exactly the method that I used on my previous job)

- But, unfourtunately, I had not really much experience exactly with this, it was mostly done by our Senior Developers, but I am ready to learn

Optimize performance:

- To optimize the perfomance, I would firstly take a look at all queries (also using ANALYZE) and then I would think how to improve them (CTE, Indexing, avoiding unneccesary joins, configuring the WHERE statements, etc.)