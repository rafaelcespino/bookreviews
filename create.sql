CREATE TABLE books (
    book_id SERIAL PRIMARY KEY,
    author VARCHAR NOT NULL,
    title VARCHAR NOT NULL,
    ISBN INTEGER NOT NULL,
    year INTEGER NOT NULL
);

CREATE TABLE users (
    user_id SERIAL NOT NULL PRIMARY KEY,
    username VARCHAR NOT NULL,
    password VARCHAR NOT NULL,
    name VARCHAR NOT NULL
);

CREATE TABLE reviews (
    review_id SERIAL NOT NULL PRIMARY KEY,
    review VARCHAR(500) NOT NULL,
    user_id INTEGER NOT NULL,
    book_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (book_id) REFERENCES books(book_id)
);