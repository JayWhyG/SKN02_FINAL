# SKN02_FINAL_1Team
AI 모의면접 서비스
<br />

## 🎤 팀 호영희(HYH)
<table>
  <tr>
    <th>HYH</th>
    <th>김은종</th>
    <th>강민호</th>
    <th>박주희</th>
    <th>장준영</th>
    <th>정우영</th>
  </tr>
  <tr>
    <td><img src="https://github.com/user-attachments/assets/d06b6aae-3ece-465e-b24a-f6591b7a267a" width="100px" alt="호영희 이미지"></td>
    <td><img src="https://github.com/user-attachments/assets/861bd8c6-78fa-4006-a819-1b2d0d7e3911" width="100px" alt="김은종 이미지"></td>
    <td><img src="https://github.com/user-attachments/assets/5d8c6d55-40ca-4769-b2fe-47ded1fd826d" width="100px" alt="강민호 이미지"></td>
    <td align="center"><img src="https://github.com/user-attachments/assets/03da861f-b44b-4032-882f-e3fe8383d1cd" width="100px" alt="박주희 이미지" ></td>
    <td align="center"><img src="https://github.com/user-attachments/assets/d6987aeb-094d-4b88-b31b-3ab674b9c273" width="100px" alt="장준영 이미지"></td>
    <td><img src="https://github.com/user-attachments/assets/6bbbbb65-1635-4088-a764-0d8d4f6f7618" width="100px" alt="정우영 이미지"></td>
  </tr>
  <tr>
    <td align="center">팀 로고</td>
    <td align="center">멘토</td>
    <td align="center">PM<br>모델 설계 </td>
    <td align="center">데이터 수집 및 전처리<br>DB 구현</td>
    <td align="center">웹서버 구축 및 구현<br>디자인 설계</td>
    <td align="center">문서화<br>디자인 설계</td>

  </tr>
</table>


<br></br>
## 📑 프로젝트 개요
- 프로젝트명: 지원자의 이력서를 기반으로 지원 기업 맞춤 정보를 활용한 실전 대비 AI 모의면접 시스템

### 서비스 목표
- 사용자의 이력서와 자소서를 기반으로 기업 맞춤형 질문 제공
- AI 면접관을 통해 실전 면접 대비 환경 제공
- 면접 종료 후 성과 분석 및 피드백 제공

### 주요 기능

1. **이력서 기반 맞춤형 질문 생성**
   - 사용자가 업로드한 이력서 및 자소서를 분석하여 기업과 직무에 맞는 질문을 LLM 에이전트가 자동 생성.

2. **실시간 AI 면접 진행 및 피드백 제공**
   - AI 면접관이 실시간으로 질문하고, 사용자의 답변에 대해 평가 및 맞춤 피드백을 제공.
  
3. **면접 기록 및 분석 관리**
   - 면접 기록과 결과를 저장하고, 사용자 계정에서 언제든지 확인할 수 있는 관리 기능 제공. 

<br />

## 🔨 기술 스택
<div align="left">

<img src="https://img.shields.io/badge/Python-blue?logo=python&logoColor=white" />
<img src="https://img.shields.io/badge/Django-092E20?logo=django&logoColor=white" />
<img src="https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white" />
<br />

<img src="https://img.shields.io/badge/HTML-E34F26?logo=html5&logoColor=white" />
<img src="https://img.shields.io/badge/CSS-blue?logo=css3&logoColor=white" />
<img src="https://img.shields.io/badge/JavaScript-yellow?logo=javascript&logoColor=white" />
<br />

<img src="https://img.shields.io/badge/MySQL-4479A1?logo=mysql&logoColor=white" />
<img src="https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white" />
<img src="https://img.shields.io/badge/AWS-FF9900?logo=amazonaws&logoColor=white" />

</div>


<br />

## 📝 WBS
<img src="https://github.com/user-attachments/assets/3985013d-192f-4d56-8497-ac58077aa970" alt="wbs" width="800px">

<br />
<br />

## ✅ 요구사항 명세서
### 1. 기능적 요구사항
- 시스템은 사용자가 업로드한 이력서와 자기소개서를 분석해야 한다.
- 시스템은 분석된 이력서 및 자기소개서 내용을 바탕으로 지원 직무와 관련된 맞춤형 질문을 생성해야 한다.
- 사용자가 원하는 난이도(기본, 실무, 심화)를 선택할 수 있도록 해야 한다.
- 사용자가 원하는 모의면접관 태도(유연,일반, 압박)를 선택할 수 있도록 해야 한다.
- AI 면접관이 사용자의 답변에 대해 실시간으로 반응할 수 있어야 한다.
- 사용자가 스스로 면접을 종료할 수 있는 옵션을 제공해야 한다.
- 면접 종료 후 사용자의 답변을 바탕으로 성과를 분석하고, 개선이 필요한 부분에 대한 피드백을 제공해야 한다.
- 피드백은 긍정적인 측면과 개선이 필요한 측면으로 구분하여 제공해야 한다.

### 2. 비기능적 요구사항
- 사용자 인터페이스(UI)는 직관적이고 간단하여, 사용자가 복잡한 절차 없이 서비스를 이용할 수 있어야 한다.
- 추가적인 기업별 맞춤 질문 및 면접 스타일(압박 면접 등)을 추가할 수 있어야 한다.

### 3. 인터페이스 요구사항
- 사용자 인터페이스(UI)
  - 이력서 및 자소서 업로드 페이지
  - 맞춤형 질문 면접 진행 페이지
  - 면접 종료 후 성과 및 피드백 제공 페이지
- 시스템 인터페이스
  - 이력서 및 자소서 데이터 처리 AI 모델과 연동
  - 피드백 및 성과 분석 데이터베이스와 연동

### 4. 데이터 요구사항
- 사용자의 이력서와 자소서를 저장할 데이터베이스가 필요하다.
- 면접 진행 중 생성된 답변 데이터는 추후 피드백 제공을 위해 저장되어야 한다.
### 5. **향후 확장계획**
- 영상 인식 기능을 추가하여 사용자 행동 분석 및 피드백의 정확도를 높일 예정.
- 데이터 수집 자동화를 통해 기업과 직무의 범위를 확장. 

<br />

## 💻 DB 테이블
<img src="https://github.com/user-attachments/assets/1e17bbdc-8077-47b1-9598-c659bb3bc466" alt="erd" width="800px">
<br />

## 📚 시스템 아키텍처
<img src="https://github.com/user-attachments/assets/ca7fc09c-fe7c-476d-9ac9-e941f8714681" alt="sa" width="800px">

<br />

## 🖥️ 수행결과
<details>
  <summary>1. 메인화면</summary>
  
  - '지금 시작하기' 클릭 시 로그인 창으로 이동
  
  
</details>

<details>
  <summary>2. 로그인/회원가입 화면</summary>
  
  - 아이디와 비밀번호 입력 후 '로그인' 버튼 클릭 시 로그인 진행
  - '회원가입' 버튼 클릭 시 이용약관 동의 후 진행 가능
  - '아이디 찾기'버튼 클릭 후 가입된 이메일 입력 시 해당 아이디를 찾을 수 있음.

  
</details>

<details>
  <summary>3. 면접 진행 화면</summary>
  
  - 사용자는 이력서 업로드, 면접 난이도 및 면접관 태도/기업 및 직무 등을 선택할 수 있음
  - 면접 진행 중
  - '결과 보기' 버튼 클릭 시 피드백 화면으로 이동

  
</details>

<details>
  <summary>4. 면접 피드백 화면</summary>
  
  - 면접 종료 후 모범 답안 및 면접의 총점, 피드백 등을 제공
    
  
</details>

