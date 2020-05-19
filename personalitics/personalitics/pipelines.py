import sqlite3

class PersonaliticsPipeline:
	def __init__(self):
		self.create_connection()

	def create_connection(self):
		self.conn = sqlite3.connect('output/project_mbti.db')
		self.cursor = self.conn.cursor()
	
	def close_spider(self, spider):
		self.conn.close()
    
	def process_item(self, item, spider):
		# self.insert_to_db(item)
		return item

	def insert_to_db(self, item):
		insert_statement = '''INSERT INTO personalitics 
		(`topic`, `user_id`, `user_type`, `parent_text`, `child_text`, `date`,
		 `source`, `project`, `spider`, `server`, `created_at`)
		 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
		 '''
		# item = [i[0] for i in item]
		values = (item['topic'][0], item['user_id'][0], item['user_type'][0],
				  item['parent_text'][0], item['child_text'][0], item['date'][0],
				  item['source'][0], item['project'][0], item['spider'][0],
				  item['server'][0], item['created_at'])
		self.cursor.execute(insert_statement, values)
		self.conn.commit()


'''
CREATE TABLE personalitics(
id INTEGER PRIMARY KEY AUTOINCREMENT ,`topic` CHAR(256), `user_id` CHAR(64), `user_type` CHAR(64), `parent_text` TEXT, `child_text` TEXT, `date` CHAR(64),
 `source` CHAR(256), `project` CHAR(32), `spider` CHAR(32), `server` CHAR(32), `created_at` CHAR(64)
);
'''


