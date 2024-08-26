Hamonsoft AI Team 공통 모듈
=============================

- 공통 으로 사용될 모듈은 pypi-source/ 하위에 디렉토리 경로로 관리 한다.
- 각 모듈의 setup.py은 pypi-source/[module]/ 하위에 관리 한다.

## 모듈 빌드

- 모듈 빌드는 아래와 같이 진행 한다.

``` bash
$ cd [모듈]
$ python setup.py sdist
```

---

## 업로드 설정 [pypi]

- https://packaging.python.org/en/latest/specifications/pypirc/
- ~/.pypirc 파일을 생성 한다.
- 아래와 같이 설정 한다.

``` bash
[pypi]
username = __token__
password = [API_TOKEN]
```

---

## 업로드

- pypi 업로드는 아래와 같이 진행 한다.

``` bash
$ python setup.py sdist --formats=gztar
```

> **Note** pypirc 파일을 생성 하지 않을 경우
> ``` bash
> $ export TWINE_USERNAME=__token__
> $ export TWINE_PASSWORD={api-token}
> ```

```bash
$ twine upload -r pypi dist/*
```

> **Warning**
> 업로드 시 dist/ 디렉토리에 있는 파일을 모두 업로드 한다.

