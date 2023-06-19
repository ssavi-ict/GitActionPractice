import json
import os.path
import time
import requests
from bs4 import BeautifulSoup
from config import CONFIG
import os
import git


class GitOps:

    def __init__(self):
        self.repo_directory = os.getcwd()
        self.remote_name = "origin"
        self.branch_name = "main"
        self.file_to_track = "contests.json"

    # Git pull to fetch the recent changes
    def git_pull(self):
        repo = git.Repo(self.repo_directory)
        origin = repo.remote(self.remote_name)
        origin.pull(self.branch_name)

    # Git add the file if changes are detected
    def git_add_file(self):
        repo = git.Repo(self.repo_directory)
        repo.index.add([self.file_to_track])

    # Git commit the changes with a message
    def git_commit(self, message):
        repo = git.Repo(self.repo_directory)
        repo.index.commit(message)

    # Raise a pull request using GitHub API
    def raise_pull_request(self):
        url = f"https://api.github.com/repos/{self.remote_name}/{self.repo_directory}/pulls"
        headers = {"Authorization": "token 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"}

        payload = {
            "title": "Pull Request Title",
            "body": "Pull Request Description",
            "head": "your-branch",
            "base": self.branch_name
        }

        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 201:
            print("Pull request raised successfully.")
        else:
            print("Failed to raise pull request.")

    # Check if there are changes in the file
    def has_changes(self):
        repo = git.Repo(self.repo_directory)
        return repo.is_dirty(path=self.file_to_track)

    # Check if the Git repository is clean
    def is_repository_clean(self):
        repo = git.Repo(self.repo_directory)
        return not repo.is_dirty()

    # Run the Git operations
    def run_git_operations(self, commit_message):
        # self.git_pull()
        if self.has_changes():
            self.git_add_file()
            self.git_commit(commit_message)
            if self.is_repository_clean():
                self.raise_pull_request()
            else:
                print("Repository is not clean after commit.")
        else:
            print("No changes detected.")

    # Example usage
    # commit_message = "Commit message for the changes"
    # run_git_operations(commit_message)


class CONTEST(object):
    def __init__(self, contest_info_path):
        self.contest_info_path = contest_info_path

    # noinspection PyMethodMayBeStatic
    def get_all_urls(self):
        reqs = requests.get(url=CONFIG.CONTEST_ROOT_URL)
        b_soup = BeautifulSoup(reqs.text, 'html.parser')
        all_urls = []
        for href in b_soup.find_all('a'):
            all_urls.append(href.get('href'))
        return all_urls

    # noinspection PyMethodMayBeStatic
    def filter_contest_url(self):
        all_urls = self.get_all_urls()
        contest_urls = []
        for url in all_urls:
            for tag in CONFIG.CONTEST_FILTERING_TAG:
                if url and tag in url:
                    url = url.split("/")[-1]
                    contest_urls.append(url)
        contest_urls = list(dict.fromkeys(contest_urls))
        return contest_urls

    def filter_valid_contests(self):
        contest_slugs = self.filter_contest_url()
        valid_contests = {}

        for slug in contest_slugs:
            formed_url = CONFIG.CONTEST_API_ENDPOINT + slug
            response = requests.get(formed_url)
            response_json = response.json()
            is_private = response_json["contest"]["is_private"]
            contest_start_time = response_json["contest"]["start_time"]
            contest_title = response_json["contest"]["title"]
            if is_private or int(time.time()) > int(contest_start_time):
                print("[ " + str(is_private) + " ]", contest_title, ' is private ... ')
                continue
            contest_duration = response_json["contest"]["duration"]
            # print(contest_title, contest_start_time, contest_duration, is_virtual, is_private)
            contest_info = {
                "title": contest_title, "start_time": contest_start_time, "contest_duration": contest_duration
            }
            valid_contests[slug] = contest_info
        return valid_contests

    # noinspection PyMethodMayBeStatic
    def store_valid_contests_in_json(self):
        contests = self.filter_valid_contests()
        print(contests)
        # self.create_a_contest_json()
        with open(self.contest_info_path, 'w') as file:
            json.dump(contests, file)
        time.sleep(1.0)
        with open(self.contest_info_path, 'r') as f:
            data = json.load(f)
        print(data)

    # noinspection PyMethodMayBeStatic
    def create_a_contest_json(self):
        if os.path.exists(self.contest_info_path):
            os.remove(self.contest_info_path)

        with open(self.contest_info_path, 'w') as file:
            json.dump({}, file)


if __name__ == '__main__':
    current_path = os.path.dirname(os.path.abspath(__file__))

    # current_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    data_path = os.path.join(current_path, 'data')
    contest_info_json_path = os.path.join(data_path, 'contests.json')
    git_ops = GitOps()
    git_ops.git_pull()
    time.sleep(1.0)
    contest = CONTEST(contest_info_path=contest_info_json_path)
    contest.store_valid_contests_in_json()
    time.sleep(2.0)
    git_ops.run_git_operations(commit_message='Automated Pull Request')

# all_url = ['/', '/explore/', '/problemset/all/', '/contest/', '/discuss/', '/', None, '/contest/weekly-contest-350', '/contest/biweekly-contest-107', '/business/contact/', '/contest/weekly-contest-291', '/contest/weekly-contest-290', '/contest/biweekly-contest-85', '/contest/weekly-contest-349', None, '/contest/biweekly-contest-106', None, '/contest/weekly-contest-348', None, '/contest/weekly-contest-347', None, '/contest/biweekly-contest-105', None, '/contest/weekly-contest-346', None, '/contest/weekly-contest-345', None, '/contest/biweekly-contest-104', None, '/contest/weekly-contest-344', None, '/contest/weekly-contest-343', None, '/neal_wu', 'https://leetcode.cn/u/Heltion', 'https://leetcode.cn/u/JOHNKRAM', '/numb3r5', 'https://leetcode.cn/u/int65536', 'https://leetcode.cn/u/arignote', '/hank55663', '/xiaowuc1', '/qeetcode', '/AntonRaichuk', '/contest/globalranking', '/support/', '/jobs/', '/bugbounty/', '/interview/', '/student/', '/terms/', '/privacy/', '/region/']
