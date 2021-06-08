# < EM 알고리즘 기반 이모티콘 선호도 분석 >

- Member : 최규형,이정현,지정원
- Status : Complete
- Term : 2021.04.16~2021.06.03
- Tag : Project
-  Collaboratory Company : [글로벌 이모티콘 플랫폼 기업 Mojitok](https://stickerfarm.mojitok.com/)


## 1. Background

- 일상 의사소통에서 이모티콘의 사용이 지속적으로 증가하며 이모티콘 전성시대라고 해도 과언이 아니다. 
- 홍수처럼 쏟아져 나오는 이모티콘들을 사용자가 보다 편리하게 접하고 이용할 수 있도록  **좀 더 잘 추천하는 방법**을 찾아보고자 한다.

## 2. Problem to Solution
### Problem
**많이 클릭되었다면 무조건 인기있는 이모티콘일까?**
- 스티커 인기도는 일반적으로 계산이 간단한 클릭율로 판단하는데,  **같은 스티커여도 위치가 달라지면 클릭율도 달라진다**. 
- 이는 **기존의 클릭율이 스티커의 선호도를 잘 반영하지 못한다**는 점을 보여준다.
![Problem2](https://user-images.githubusercontent.com/54830788/121119375-7627e200-c856-11eb-8b12-bab59ac5a107.png)


### Solution
![Solution](https://user-images.githubusercontent.com/54830788/121118281-88088580-c854-11eb-880a-8a09c9a23972.PNG)
 [2018년 구글 논문 (Position Bias Estimation for Unbiased Learning to Rank in Personal Search)](https://static.googleusercontent.com/media/research.google.com/ko//pubs/archive/46485.pdf)을 벤치마킹한 **통계 기반 머신러닝**을 적용하여 **이모티콘 선호도와 위치 영향력을 분리 추정**


## 3. Research

### Research Process
![Research Process](https://user-images.githubusercontent.com/54830788/121118280-88088580-c854-11eb-93aa-a0616a643ca6.PNG)

### Em Algorithm Implementation Research
![Implementation](https://user-images.githubusercontent.com/54830788/121118274-86d75880-c854-11eb-93fd-3a6a9fc8b951.PNG)

## 4. Data 
[모지톡(mojitok)](https://stickerfarm.mojitok.com/)으로부터 제공받은 Google Analytics 데이터와 User DB 데이터 이용
|컬럼|의미|예시|
|:------:|-----------|------|
|data|일자|2021-03-01
|time|시간|00:46:33
|cs-uri-query| t = 스티커 타입,<br> p = 미리보기,<br> c = 전송용 선택 |'t=T&p=["sticker1",1,"sticker2",40,"sticker3",3]&c=["sticker1",1]&m=KT' -H 'mojitok-token: r:c54da4d71fb4263a11bd26bg826g0d79'  |


## 5. Implementation
 
 ### Task Flow![taskflow](https://user-images.githubusercontent.com/54830788/121118282-88a11c00-c854-11eb-8691-88bcea9ae84a.PNG )
 ### Preprocessing 
![preprocess](https://user-images.githubusercontent.com/54830788/121118276-876fef00-c854-11eb-9e45-8dcd66e8ed03.PNG)
### Algorithm Implementation
![EM_Implementation](https://user-images.githubusercontent.com/54830788/121118272-85a62b80-c854-11eb-871c-2b5400f06be0.PNG)

## 6. Result

## 7. Analysis

### Insight :  Click-rate vs. EM Algorithm

1.  두 분석 기법은 각각의 한계점을 가지고 있음
	- (click-rate 기반) 스티커와 위치 선호도가 분리되지 않음
	- (EM Algorithm 기반) 단순화된 가정 사용으로 현실 규칙을 100% 설명 불가

2. 그럼에도 두 분석 기법의 결과 간에 유의미한 차이가 있었음
	- EM Algorithm 기반 위치 영향력 분석 결과가 UI / UX 관점에서 더 높은 설명력을 가짐
	- 스티커 선호도와 위치 영향력 분리가 기대한 대로 수행되었다고 볼 수 있음
	
3. EM Algorithm 기반으로 추천 이모티콘 목록을 생성 가능
	- 기존에는 click-rate 기반으로 이모티콘 선호도를 측정하여 인기 이모티콘으로 소개
	- EM Algorithm 기반 추천 이모티콘 목록을 생성한다면 더 효과적일 것으로 기대할 수 있음
	
## 8.Conclusion

### 활용 방안
위치 영향력과 스티커 선호도를 구분한 수치를 활용하면 먼저 **1.기존의 알고리즘을 유저 선호를 정밀하게 반영하도록 개선**할 수 있고  **2. 수치에 기반한 위치 영향력**을 역으로 이용하여 팔고 싶은, 홍보하고 싶은 스티커를 특정 위치에 배치할 수 있습니다. 또한 이후에 개선된 **3. 추천 시스템을 만드는  baseline을 확립**한다고 볼 수 있습니다.


 
## 9. How to Run

### Data Crawling
 aaa.py
### Preprocessing
aaa.py
### Implementation(EM Algorithm)

### Test by Toy Dataset Modeling
  


