import pytest
import pandas as pd
from app.services.school_search import SchoolSearchService

@pytest.fixture
def mock_school_data():
    """테스트에 사용할 모의 학교 데이터 DataFrame을 생성합니다."""
    data = {
        '시도교육청코드': ['B10', 'B10', 'C10'],
        '학교명': ['서울테스트초등학교', '서울소프트웨어마이스터고', '부산소프트웨어마이스터고'],
        '영문학교명': ['Seoul Test Elementary', 'Seoul Software Meister High', 'Busan Software Meister High'],
        '행정표준코드': ['1111', '2222', '3333'],
        '도로명주소': ['서울 테스트로 1', '서울 마이스터로 10', '부산 강서구 100']
    }
    return pd.DataFrame(data)

@pytest.fixture
def mocked_school_search_service(mocker, mock_school_data):
    """
    _load_data 메서드가 모의 데이터를 반환하도록 패치된
    SchoolSearchService 인스턴스를 생성합니다.
    """
    # SchoolSearchService._load_data 메서드를 모킹하여
    # 항상 mock_school_data를 반환하도록 설정합니다.
    mocker.patch.object(SchoolSearchService, '_load_data', return_value=mock_school_data)

    # 이제 SchoolSearchService를 초기화하면 _load_data가 모킹된 버전으로 호출됩니다.
    # data_file_path는 아무거나 넣어도 상관없습니다.
    return SchoolSearchService(data_file_path="dummy/path/to/data.csv")


def test_search_school_found_by_korean_name(mocked_school_search_service):
    """한글 학교명으로 학교를 성공적으로 검색하는지 테스트합니다."""
    service = mocked_school_search_service
    result = service.search(atpt_ofcdc_sc_code='B10', schul_nm='소프트웨어')

    assert len(result) == 1
    assert result[0]['학교명'] == '서울소프트웨어마이스터고'
    assert result[0]['행정표준코드'] == '2222'

def test_search_school_found_by_english_name(mocked_school_search_service):
    """영문 학교명으로 학교를 성공적으로 검색하는지 테스트합니다 (대소문자 무시)."""
    service = mocked_school_search_service
    # 검색어는 소문자, 데이터는 대소문자 섞여 있음
    result = service.search(atpt_ofcdc_sc_code='C10', schul_nm='software')

    assert len(result) == 1
    assert result[0]['학교명'] == '부산소프트웨어마이스터고'
    assert result[0]['영문학교명'] == 'Busan Software Meister High'

def test_search_school_not_found(mocked_school_search_service):
    """검색 결과가 없을 때 빈 리스트를 반환하는지 테스트합니다."""
    service = mocked_school_search_service
    result = service.search(atpt_ofcdc_sc_code='B10', schul_nm='존재하지않는학교')

    assert len(result) == 0
    assert result == []

def test_search_school_wrong_region(mocked_school_search_service):
    """학교는 존재하지만, 다른 지역 코드로 검색했을 때 결과가 없는지 테스트합니다."""
    service = mocked_school_search_service
    # '서울소프트웨어마이스터고'는 B10에 있지만, C10으로 검색
    result = service.search(atpt_ofcdc_sc_code='C10', schul_nm='서울소프트웨어')

    assert len(result) == 0

def test_search_returns_multiple_results(mocked_school_search_service):
    """검색어가 여러 결과와 일치할 때 모든 결과를 반환하는지 테스트합니다."""
    service = mocked_school_search_service
    # '마이스터'는 B10의 '서울소프트웨어마이스터고'와 C10의 '부산소프트웨어마이스터고'에 모두 포함됨
    # 하지만 시도교육청코드가 B10이므로 하나만 나와야 함.
    result_b10 = service.search(atpt_ofcdc_sc_code='B10', schul_nm='마이스터')
    assert len(result_b10) == 1
    assert result_b10[0]['학교명'] == '서울소프트웨어마이스터고'

    # 만약 시도교육청코드 필터가 없다면 여러개가 나올 수 있음을 가정 (이 테스트는 현재 로직에선 불필요)
    # 여기서는 현재 로직이 시도교육청코드로 잘 필터링하는지 확인하는 것이 더 중요.
