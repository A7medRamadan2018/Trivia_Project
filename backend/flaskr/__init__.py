import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

  '''
  Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
  '''
  Use the after_request decorator to set Access-Control-Allow
  '''
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,POST,PATCH,DELETE,OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response

    '''
  
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
    @app.route('/api/questions/categories', methods=['GET'])
    def get_categories():
        categories = Category.query.all()
        all_categories = {catg.id: catg.type for catg in categories}
        if len(all_categories) == 0:
            abort(404)

        return jsonify({
            'categories': all_categories,
            'success': True
        })

    @app.route('/api/categories', methods=['GET'])
    def get_all_categories():
        categories = Category.query.all()
        all_categories = {catg.id: catg.type for catg in categories}
        if len(all_categories) == 0:
            abort(404)
        return jsonify({
            'categories': all_categories,
            'success': True
        })

    '''
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''

    def paginate_questions(request, selection):
        page = request.args.get('page', 1, type=int)
        start = (page-1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE
        current_questions = [q.format() for q in selection]
        return current_questions[start:end]

    @app.route('/api/questions', methods=['GET'])
    def get_questions():
        all_questions = Question.query.all()

        current_questions = paginate_questions(request, all_questions)
        if len(current_questions) == 0:
            abort(404)
        categories = Category.query.all()
        all_categories = {catg.id: catg.type for catg in categories}

        return jsonify({
            'questions': current_questions,
            'total_questions': len(all_questions),
            'categories': all_categories,
            'current_category': None,
            'success': True
        })

    '''
  
  Create an endpoint to DELETE question using a question ID. 
  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
    @app.route('/api/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.get(question_id)
            question.delete()

            return jsonify({
                'success': True,
            })

        except Exception as err:
            abort(422)
    '''
  
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
    @app.route('/api/questions', methods=['POST'])
    def create_question():
        data = request.get_json()
        question = data.get('question', None)
        answer = data.get('answer', None)
        category = data.get('category', None)
        difficulty = data.get('difficulty', None)
        try:
            question = Question(question=question, answer=answer,
                                category=category, difficulty=difficulty)
            question.insert()
            selection = Question.query.all()
            print(len(selection))
            if len(selection) == 0:
                abort(404)
            current_questions = paginate_questions(request, selection)
            categories = Category.query.all()
            all_categories = {catg.id: catg.type for catg in categories}

            return jsonify({
                'questions': current_questions,
                'total_questions': len(selection),
                'categories': all_categories,
                'current_category': None,
                'success': True
            })
        except:
            abort(422)

    '''
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
    @app.route('/api/questions/search', methods=['POST'])
    def get_questions_baesd_on_searchTerm():

        try:
            search_term = request.get_json().get('searchTerm')
            questions = Question.query.filter(
                Question.question.ilike("%"+search_term+"%")).all()
            current_questions = paginate_questions(request, questions)
            if len(current_questions) == 0:
                abort(404)
            return jsonify({
                'questions': current_questions,
                'total_questions': len(questions),
                'current_category': None,
                'success': True
            })
        except:
            abort(422)
    '''
  Create a GET endpoint to get questions based on category. 
  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
    @app.route('/api/categories/<category_id>/questions', methods=['GET'])
    def get_question_by_category(category_id):
        try:
            questions = Question.query.filter_by(category=category_id).all()
            current_questions = paginate_questions(request, questions)
            if len(current_questions) == 0:
                abort(404)

            return jsonify({
                'questions': current_questions,
                'total_questions': len(questions),
                'current_category': category_id,
                'success': True
            })
        except:
            abort(422)

    '''
  
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
    @app.route('/api/quizzes', methods=['POST'])
    def play_quiz():
        data = request.get_json()
        category = data.get('quiz_category')
        previous_questions = data.get('previous_questions')
        try:
            if category['id'] == 0:
                questions = Question.query.filter(
                    Question.id.notin_(previous_questions)).all()

            else:
                questions = Question.query.filter_by(category=category['id']).filter(
                    Question.id.notin_(previous_questions)).all()

            if len(questions) == 0:
                abort(404)
            current_question = random.choice(questions)

            return jsonify({
                'success': True,
                'question': current_question.format(),
            })

        except:
            abort(422)

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "Bad Request"
        }), 400

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "Method Not Allowed"
        }), 405

    return app
