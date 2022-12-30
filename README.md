# Bookie

#### Video Demo: https://www.youtube.com/watch?v=CVrOaTUgP6E

#### Description: Bookie is a simle book tracking web app

The backend was written in Python, along with Flask and a local SQLite database.
The frontend was written in simple CSS and Javascript, along with a bit of Bootstrap.

In the /static folder you'll find the favicon that is used for the website, along with styles.css for the whole styling used, and script.js, which was left empty.
In the /templates directory you'll find the bulk of the HTML work.

The most important file in there is the layout file, layout.html.
Inside are a bunch of links to external libraries and the navbar that gets shown on every page.

The next most important file is index.html, which is the homepage. The homepage contains the aforementioned navbar, a neat tracker for showing how many books you have in each category and the functionality for managing all of your books.

The search function is very similar to the one described in Week 9, but instead of showing a simple list, it shows a table with a bit of Javascript work done behind the curtains.
Basically, once the page loads, it already contains a table for showing all of the books along with their information, but the table is empty. Once the user starts typing either a book or an author they want to search for, and input event listener will wait until he has typed at least 3 characters (as to not start showing a really long table at first). If whatever the user typed exists in the database, the app will go to /search and query for the entered terms. The route /search, described in app.py simply looks in databse for the entered terms and returns a jsonified list back to the current javascript block I'm describing. If the json isn't empty, the app will format the results and start populating the table, along with making it visible.

On the homepage, the user also has the posibility to add a book. The button calls for a simple Bootstrap collapse that will hide the other elements in order for them to not overlap each other. There will also be some basic form checking done to make sure that sure has enter valid information and when the "Add" button is pressed, everything gets passed over to Flask in the @addbook route, which will add the details to the database.

Also, on the same page, after the user has searched for a book, he can edit any of it's details and either add or edit any currently existing review. This is the only place in the whole app where a GET method is used instead of POST. When the used clicks the book they want to edit, the ID of the said book gets passed as a GET parameter to render the editbook.html page.

The tracker for showing the current amount of books in each category is pretty simlpe by design, combining some simple Python and Jinja.

Both login.html and register.html contain some simple forms for registering or loging in the user, with all of the validation being done by Python and Flask.

logout.html and search.html are some simple files I've used for testing and serve no purpose other than troubleshooting.

addbook.html and editbook.html are another set of simple pages containing some forms that are validated by Python. The only exception is that editbook.html also has information passed to it when the file loads, to show the user the current book's details, before editing them.

reviews.html is, as the name implies, the page that gets shown when the users wants to view all of his reviews for the books. There is a simple html table that gets populated by a Jinja for each loop.

stats.html was a little more complicated for me to write, as the page contains some fancy Carousel cards, along with collapses and a progress bar. The carousel cards get populated once again, by combining Python and Jinja. Depending on your current IDE, you may find that there is an error on line 94, even though everything works fine. That's because I had to use some ugly formatting. In order for the bar to update accoring the books the user has read, the numbers are getting passed from Python, but instead of showing some text on the page as I've done before with Jinja, they are going straight into a "style" tag that has a width attribute. That width attribute is the way the bar gets updated.

The biggest file by comparison to the rest is app.py, where the whole backend of the application lies. I've tried commenting as much as possible, but in short, every route gets handled in there, along with deciding which page to load and when.
