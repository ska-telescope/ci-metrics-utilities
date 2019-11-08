python3 scripts/collect_metrics.py
mkdir -p build/badges
apt-get -y update
apt-get install -y python3-pip
pip3 install --user anybadge
python3 scripts/create_badges.py
find build/badges -type f -exec curl --user $RAW_USER:$RAW_PASS --upload-file {} $RAW_HOST/repository/raw/gitlab-ci-metrics/$CI_PROJECT_PATH/$CI_COMMIT_REF_NAME/badges/ \;
find build/reports -type f -exec curl --user $RAW_USER:$RAW_PASS --upload-file {} $RAW_HOST/repository/raw/gitlab-ci-metrics/$CI_PROJECT_PATH/$CI_COMMIT_REF_NAME/reports/ \;