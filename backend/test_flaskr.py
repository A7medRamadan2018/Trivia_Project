import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}:{}@{}/{}".format('postgres', 'ahmed@1234','localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

        self.new_question={
            "question":"How many week days",
            "answer":"7",
            "difficulty":2,
            "category":"2"
        }
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    Write at least one test for each test for successful operation and for expected errors.
    """

    ''' Testing for retreive Quesions'''
    def test_get_paginated_question(self):
        res = self.client().get('/api/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(len(data['categories']))
        self.assertEqual(data['current_category'],None)

    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get('/api/questions?page=1000')
        data_ = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data_['success'], False)
        self.assertEqual(data_['message'], 'Not found')
    
    # ''' Testing for Deleting Quesions'''
    # def test_delete_question(self):
    #     res = self.client().delete('/api/questions/10')
    #     data = json.loads(res.data)

    #     question = Question.query.filter(Question.id == 9).one_or_none()

    #     self.assertEqual(res.status_code, 200)
    #     self.assertEqual(data['success'], True)
            

    def test_if_question_does_not_exist(self):
        res = self.client().delete('/api/questions/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    ''' Testing for Create Quesions'''
    def test_create_new_question(self):
        res = self.client().post('/api/questions', json=self.new_question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

        self.assertTrue(data['questions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])
        self.assertEqual(data['current_category'],None)

    ''' Testing for retrive Quesions based on search Term'''
    def test_get_questions_baesd_on_searchTerm(self):
        res = self.client().post('/api/questions', json={'searchTerm':'what'})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertEqual(data['current_category'],None)

    def test_if_get_questions_baesd_on_searchTerm_not_exist(self):
        res = self.client().post('/api/questions/search', json={'searchTerm':'udacity'})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    ''' Testing for retrive Quesions based on a category'''
    def test_get_question_by_category(self):
        res = self.client().get('/api/categories/2/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['current_category'])
        self.assertEqual(data['success'], True)

    def test_if_get_question_by_category_not_found(self):
        res = self.client().get('/api/categories/100/questions', json={'category':'100'})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    ''' Testing for playing Quiz'''
    def test_play_quiz(self):
        res = self.client().post('/api/quizzes',json={'quiz_category':{'id':"1",'type':'Science'},'previous_questions':[]})
        
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['question'])
        self.assertEqual(data['success'], True)

    def test_play_quiz_if_category_not_found(self):
        res = self.client().post('/api/quizzes',json={'quiz_category':{'id':"3000",'type':'math'},'previous_questions':[]})
        
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')
       
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()