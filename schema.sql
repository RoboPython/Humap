create table points_of_interest (
	id integer primary key autoincrement,
	lat REAL,
	lng REAL,
	icon_location TEXT,
	name TEXT,
	category TEXT
);