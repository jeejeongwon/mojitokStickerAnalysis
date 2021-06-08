import numpy as np
import pickle

def em_algorithm_inference(result, seed_num=2021):
    # 랜덤 시드 지정
    np.random.seed(seed_num)

    # 업데이트 파라미터 초기화
    theta_0, gamma_0 = np.random.rand(), np.random.rand()

    # 업데이트한 파라미터를 저장할 딕셔너리
    parameter_dict = {'theta_k_numerator':{},
                      'theta_k_denominator':{},
                      'gamma_qd_numerator':{},
                      'gamma_qd_denominator':{},
                       'theta_k':{},
                      'gamma_qd':{}}

    # while loop 종료 조건
    # 파라미터 업데이트가 매우 작은 수준으로 일어나면 수렴으로 판단함
    parameter_threshold = 0.000001
    threshold_hit = False

    print(f'theta init:{theta_0}, gamma init:{gamma_0}')

    while not threshold_hit:
        # 관측 데이터셋 result 딕셔너리의 key, value에 대하여
        for res_k, res_v in result.items():
            # 각각의 key token(=emoji)에 대하여
            q = res_k  # 'hello'

            # keytoken q에 대응하는 각각의 스티커에 대하여
            for d, pos_click_data in res_v.items():  # d = '3dBcidpq'
                if (q, d) not in parameter_dict['gamma_qd'].keys():
                    parameter_dict['gamma_qd'][(q, d)] = gamma_0
                gamma_qd = parameter_dict['gamma_qd'][(q, d)]

                # 프리뷰 리스트의 각 위치에 있는 각각의 스티커에 대하여
                # 0, 1, 2, ... , 8
                for k, click_data in pos_click_data.items():
                    # theta_k 초기값 할당 또는 이전 iteration의 계산값 가져오기
                    if k not in parameter_dict['theta_k'].keys():
                        parameter_dict['theta_k'][k] = theta_0
                    theta_k = parameter_dict['theta_k'][k]

                    # joint probability 계산
                    # 현재 iteration에서 사용할 값 /// Expectation Step
                    prob_E1_R1_C1_given_qdk = 1
                    prob_E1_R0_C0_given_qdk = theta_k * (1 - gamma_qd) / (1 - theta_k * gamma_qd)
                    prob_E0_R1_C0_given_qdk = (1 - theta_k) * gamma_qd / (1 - theta_k * gamma_qd)
                    prob_E0_R0_C0_given_qdk = (1 - theta_k) * (1 - gamma_qd) / (1 - theta_k * gamma_qd)

                    for c, freq in click_data.items():
                        param_set = (c, q, d, k)
                        sticker_freq_cqdk = freq

                        # marginalize (summation)
                        if c:  # if clicked
                            prob_E1_given_cqdk = 1
                            prob_R1_given_cqdk = 1

                        else:  # if not clicked
                            prob_E1_given_cqdk = prob_E1_R0_C0_given_qdk
                            prob_R1_given_cqdk = prob_E0_R1_C0_given_qdk

                        # theta, gamma 분자 및 분모 계산
                        theta_k_numerator = prob_E1_given_cqdk * sticker_freq_cqdk
                        theta_k_denominator = sticker_freq_cqdk
                        gamma_qd_numerator = prob_R1_given_cqdk * sticker_freq_cqdk
                        gamma_qd_denominator = sticker_freq_cqdk

                        # theta, gamma 계산값 dictionary 업데이트
                        parameter_dict['theta_k_numerator'][param_set] = theta_k_numerator
                        parameter_dict['theta_k_denominator'][param_set] = theta_k_denominator
                        parameter_dict['gamma_qd_numerator'][param_set] = gamma_qd_numerator
                        parameter_dict['gamma_qd_denominator'][param_set] = gamma_qd_denominator

        # 새로운 theta_k, gamma_qd 계산
        total_param_set = parameter_dict['theta_k_numerator'].keys()
        prev_theta_k = parameter_dict['theta_k'].copy()
        prev_gamma_qd = parameter_dict['gamma_qd'].copy()

        # parameter_dict에 단위 이터레이션 1개 정보 수집 완료
        # 직전 업데이트된 theta_k, gamma_qd으로 계산
        theta_k_update_dict, gamma_qd_update_dict = {}, {}

        for pset in total_param_set:
            clicked_, query_, sticker_, pos_ = pset[0], pset[1], pset[2], pset[3]

            ## numerator / denominator for theta_k
            numerator_theta = parameter_dict['theta_k_numerator'][pset]
            denominator_theta = parameter_dict['theta_k_denominator'][pset]

            ## numerator / denominator for gamma_qd
            numerator_gamma = parameter_dict['gamma_qd_numerator'][pset]
            denominator_gamma = parameter_dict['gamma_qd_denominator'][pset]

            if pos_ not in theta_k_update_dict.keys():
                theta_k_update_dict[pos_] = {'numerator': 0,
                                             'denominator': 0}
            if (query_, sticker_) not in gamma_qd_update_dict.keys():
                gamma_qd_update_dict[(query_, sticker_)] = {'numerator': 0,
                                                            'denominator': 0}

            theta_k_update_dict[pos_]['numerator'] += numerator_theta
            theta_k_update_dict[pos_]['denominator'] += denominator_theta
            gamma_qd_update_dict[(query_, sticker_)]['numerator'] += numerator_gamma
            gamma_qd_update_dict[(query_, sticker_)]['denominator'] += denominator_gamma

        #     print(theta_k_update_dict)
        #     print(gamma_qd_update_dict)
        #     break
        # theta_k, gamma_qd 업데이트
        # parameter_dict['theta_k']

        # UPDATE theta_k, gamma_qd
        for param_k in theta_k_update_dict.keys():
            numerator = theta_k_update_dict[param_k]['numerator']
            denominator = theta_k_update_dict[param_k]['denominator']
            parameter_dict['theta_k'][param_k] = numerator / denominator

        for param_qd in gamma_qd_update_dict.keys():
            numerator = gamma_qd_update_dict[param_qd]['numerator']
            denominator = gamma_qd_update_dict[param_qd]['denominator']
            parameter_dict['gamma_qd'][param_qd] = numerator / denominator

        # threshold_hit 판단
        # parameter_threshold = 0.1
        over_threshold_cnt = 0

        theta_k_keys = parameter_dict['theta_k'].keys()
        for tk in theta_k_keys:
            prev_theta = prev_theta_k[tk]
            current_theta = parameter_dict['theta_k'][tk]
            diff_theta = np.abs(prev_theta - current_theta)
            if diff_theta >= parameter_threshold:
                over_threshold_cnt += 1

        gamma_qd_keys = parameter_dict['gamma_qd'].keys()
        for gqd in gamma_qd_keys:
            prev_gamma = prev_gamma_qd[gqd]
            current_gamma = parameter_dict['gamma_qd'][gqd]
            diff_gamma = np.abs(prev_gamma - current_gamma)
            if diff_gamma >= parameter_threshold:
                over_threshold_cnt += 1

        # counter += 1
        #
        # if counter % 10000 == 0:
        #     print(counter)

        if not over_threshold_cnt:
            threshold_hit = True

            return parameter_dict
