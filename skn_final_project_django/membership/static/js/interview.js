document.addEventListener('DOMContentLoaded', function() {
    const interviewForm = document.getElementById('interviewForm');
    const interviewSection = document.getElementById('interviewSection');
    const conversation = document.getElementById('conversation');
    const userAnswerInput = document.getElementById('userAnswer');
    const sendAnswerButton = document.getElementById('sendAnswer');

    let sessionId = null;

    interviewForm.addEventListener('submit', function(event) {
        event.preventDefault();

        const formData = {
            user_id: document.getElementById('user_id').value,
            resume_id: document.getElementById('resume_id').value,
            corporate_id: document.getElementById('corporate_id').value,
            recruitment_id: document.getElementById('recruitment_id').value,
            job_id: document.getElementById('job_id').value,
            interview_style: document.getElementById('interview_style').value,
            difficulty_level: parseInt(document.getElementById('difficulty_level').value)
        };

        // 인터뷰 생성 요청 보내기
        fetch('api_url/interview/create_interview/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        })
        .then(response => response.json())
        .then(data => {
            sessionId = data.session_id;
            conversation.innerHTML += `<p><strong>면접관:</strong> ${data.message}</p>`;
            interviewForm.style.display = 'none';
            interviewSection.style.display = 'block';
        })
        .catch(error => {
            console.error('Error:', error);
            alert('인터뷰 생성 중 오류가 발생했습니다.');
        });
    });

    sendAnswerButton.addEventListener('click', function() {
        const userAnswer = userAnswerInput.value.trim();
        if (!userAnswer) {
            alert('답변을 입력하세요.');
            return;
        }

        const answerData = {
            user_id: sessionId,
            user_answer: userAnswer
        };

        // 답변 보내기
        fetch('api_url/interview/answer/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(answerData)
        })
        .then(response => response.json())
        .then(data => {
            // 대화 내용 업데이트
            conversation.innerHTML += `<p><strong>나:</strong> ${userAnswer}</p>`;
            conversation.innerHTML += `<p><strong>면접관:</strong> ${data.message[0]}</p>`;
            userAnswerInput.value = '';

            if (data.message[1] === 'end') {
                alert('인터뷰가 종료되었습니다.');
                sendAnswerButton.disabled = true;
                userAnswerInput.disabled = true;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('답변 처리 중 오류가 발생했습니다.');
        });
    });
});