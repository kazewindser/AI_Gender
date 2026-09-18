QUESTIONS = [
    {
        'question': 'How is your additional payment from the three main tasks calculated?',
        'choices': [
            [1, 'The sum of the payments from all three tasks'],
            [2, 'The payment from one randomly selected task'],
            [3, 'The payment from the task with the highest payment'],
            [4, 'The payment from Task 3 only'],
        ],
        'correct': 2,
        'error_msg': 'Sorry, that is incorrect. After all three main tasks are complete, one task is selected at random for payment. Your additional payment from the main tasks is the payment from that selected task.',
    },
    {
        'question': 'If the correct answer to a question is 100 and your answer is 90, how many points do you receive for that question?',
        'choices': [[1, '0 points'], [2, '5 points'], [3, '9 points'], [4, '10 points']],
        'correct': 2,
        'error_msg': 'Sorry, that is incorrect. The relative error is |90 − 100| / 100 = 0.10. The score is therefore 10 × (1 − 0.10 / 0.20) = 5 points.',
    },
    {
        'question': 'If Task 1 is selected for payment and your total score is 80 points, how much is your additional payment?',
        'choices': [
            [1, '80 yen'],
            [2, '480 yen'],
            [3, '1,920 yen'],
            [4, 'It depends on the scores of the other participants'],
        ],
        'correct': 2,
        'error_msg': 'Sorry, that is incorrect. Task 1 uses Piece rate. Your total score is converted at 6 yen per point, so your payment is 80 × 6 = 480 yen.',
    },
    {
        'question': 'Task 2 is selected for payment. Your total score is 80 points, but another participant in your group scores 100 points and has the sole highest score. How much is your additional payment?',
        'choices': [
            [1, '0 yen'],
            [2, '480 yen'],
            [3, '1,920 yen'],
            [4, 'You and the participant with the highest score split the winner’s payment equally'],
        ],
        'correct': 1,
        'error_msg': 'Sorry, that is incorrect. Task 2 uses Tournament. Participants who do not win receive 0 yen from Task 2.',
    },
    {
        'question': 'If you choose Tournament in Task 3, which scores is your Task 3 total score compared with?',
        'choices': [
            [1, 'Your own Task 2 total score'],
            [2, 'The Task 3 total score of each of the other three members of your group'],
            [3, 'The Task 2 total score of each of the other three members of your group'],
            [4, 'The average score of the other three members of your group'],
        ],
        'correct': 3,
        'error_msg': 'Sorry, that is incorrect. Your Task 3 total score is compared with the Task 2 total score of each of the other three members of your group.',
    },
    {
        'question': 'How is your total score for each task determined?',
        'choices': [
            [1, 'It depends only on the accuracy of your answers'],
            [2, 'It depends only on the number of questions for which you submit answers'],
            [3, 'It depends on both the accuracy of your answers and the number of questions you answer'],
            [4, 'It depends only on the score of your highest-scoring question'],
        ],
        'correct': 3,
        'error_msg': 'Sorry, that is incorrect. Your score for each question depends on how close your answer is to the correct answer. Your total score for each task is the sum of the scores for all questions for which you submit answers. Answering more questions that earn positive points increases your total score. Questions worth 0 points neither increase nor decrease your total score.',
    },
]
