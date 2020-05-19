from bs4 import BeautifulSoup
import re

def get_topic(string):
	'''Removes the URL part of a string ie. 
	   from: "https://www.16personalities.com/intj-personality?page=2"
	   to: "intj-personality"
	'''
	string = re.findall(r'.*\/(.+)', string)
	if len(string):
		return string
	return 

def split_parent_child(string):
	'''Split the content inside a quoted text / parent message
	   and the content of the immediate text / child message
	'''
	soup = BeautifulSoup(string)
	bbcode_element = [i.extract() for i in soup.findAll('div')]
	parent_message = [j.get_text().strip() for j in bbcode_element]
	parent_message = ' '.join(parent_message).strip()
	parent_message = remove_template_words(parent_message)
	child_message = [i.get_text().strip() for i in soup]
	child_message = ' '.join(child_message).strip()

	return parent_message, child_message

def remove_template_words(string):
	'''Remove template words from a post'''
	string = string.replace('Originally Posted by ', '')
	string = ' '.join(string.split()[1:])
	return string
