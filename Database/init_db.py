# DATABASE STRUCTURE

# ⏺ Users Table (stores user information)
#  ├─ id (PRIMARY KEY)
#  ├─ username
#  ├─ email
#  ├─ password_hash
#  └─ is_admin (0 or 1 for False/True)
#
#  Movies Table (stores movie information)
#  ├─ id (PRIMARY KEY)
#  ├─ title
#  ├─ description
#  └─ poster_url
#
#  Reviews Table (stores user reviews of movies)
#  ├─ id (PRIMARY KEY)
#  ├─ user_id (FOREIGN KEY → Users.id)
#  ├─ movie_id (FOREIGN KEY → Movies.id)
#  ├─ title
#  ├─ rating (1-5)
#  ├─ review_text
#  └─ review_date
