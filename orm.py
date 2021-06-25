import sqlite3


class DBConnector:

	def __init__(self):

		self.conn = sqlite3.connect("db.sqlite3")

		self.cur = self.conn.cursor()

		self.cur.execute("""
			CREATE TABLE IF NOT EXISTS ads(
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			category text,
			ownername text,
			phone text,
			title text,
			address text,
			city text,
			people_count int,
			description text,
			price text,
			gender text,
			userid int
			);
			""")

		self.conn.commit()

		self.cur.execute("""
			CREATE TABLE IF NOT EXISTS users(
			id INTEGER PRIMARY KEY,
			username text
			);
			""")

		self.conn.commit()

	def add_ad(self, category, ownername, phone, title, address, city, people_count, description, price, gender, user_id):
		self.cur.execute("""INSERT INTO ads(category, ownername, phone, title, address, city, people_count, description, price, gender, userid) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (category, ownername, phone, title, address, city, people_count, description, price, gender, user_id))
		self.conn.commit()
		return self.cur.lastrowid



	def get_ad(self, ad_id): 
		self.cur.execute("""SELECT * FROM ads WHERE id=(?)""", (ad_id, ))
		res = self.cur.fetchone()
		return res


	def get_all_ads(self): 
		self.cur.execute("""SELECT * FROM ads""")
		res = self.cur.fetchall()
		return res


	def get_ads_of_user(self, user_id):
		self.cur.execute("""SELECT * FROM ads WHERE userid=(?)""", (user_id, ))
		res = self.cur.fetchall()
		return res


	def delete_ad(self, ad_id):
		self.cur.execute("""DELETE FROM users WHERE id=(?)""", (ad_id, ))
		self.conn.commit()
		res = self.get_ad(ad_id)
		return res



	def add_user(self, user_id, user_name):
		self.cur.execute("""INSERT INTO users VALUES(?, ?)""", (user_id, user_name))
		self.conn.commit()
		return self.cur.lastrowid


	def get_user(self, user_id): 
		self.cur.execute("""SELECT * FROM users WHERE id=(?)""", (user_id, ))
		res = self.cur.fetchone()
		return res


	def get_all_users(self): 
		self.cur.execute("""SELECT * FROM users""")
		res = self.cur.fetchall()
		return res


	def delete_user(self, user_id):
		self.cur.execute("""DELETE FROM users WHERE id=(?)""", (user_id, ))
		self.conn.commit()
		res = self.get_ad(user_id)
		return res


if __name__ == '__main__':
	db = DBConnector()

	print(db.get_ads_of_user(840647074))
