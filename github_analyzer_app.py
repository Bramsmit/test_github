import streamlit as st
import requests
import time
from typing import Dict, List, Optional
from collections import Counter
from datetime import datetime, timezone
import calendar
import plotly.express as px
import pandas as pd

# Set page configuration
st.set_page_config(
    page_title="GitHub Profile Analyzer",
    page_icon="🔍",
    layout="wide"
)

class GitHubAnalyzer:
    def __init__(self, token: str):
        self.token = token
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        self.rate_limit_remaining = None
        self.rate_limit_reset = None

    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Makes an authenticated request with improved error handling and rate limiting."""
        if self.rate_limit_remaining is not None and self.rate_limit_remaining < 5:
            reset_time = datetime.fromtimestamp(self.rate_limit_reset, timezone.utc)
            current_time = datetime.now(timezone.utc)
            if reset_time > current_time:
                wait_seconds = (reset_time - current_time).total_seconds() + 1
                st.warning(f"Rate limit approaching. Waiting {wait_seconds:.0f} seconds...")
                time.sleep(wait_seconds)

        url = f"{self.base_url}/{endpoint}"
        try:
            response = requests.get(url, headers=self.headers, params=params)
            self.rate_limit_remaining = int(response.headers.get('X-RateLimit-Remaining', 0))
            self.rate_limit_reset = int(response.headers.get('X-RateLimit-Reset', 0))
            
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"Error {response.status_code}: {response.text}")
                return None
        except requests.exceptions.RequestException as e:
            st.error(f"Request failed: {e}")
            return None

    def get_user_info(self, username: str) -> Optional[Dict]:
        return self._make_request(f"users/{username}")

    def get_user_repos(self, username: str) -> List[Dict]:
        all_repos = []
        page = 1
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        while True:
            repos_page = self._make_request(
                f"users/{username}/repos",
                params={"page": page, "per_page": 100, "sort": "updated"}
            )
            
            if not repos_page or not isinstance(repos_page, list):
                break
                
            all_repos.extend(repos_page)
            status_text.text(f"Fetched {len(all_repos)} repositories...")
            progress_bar.progress(min(len(all_repos) / 100, 1.0))
            page += 1
            
            if len(repos_page) < 100:  # Last page
                break
        
        progress_bar.empty()
        status_text.empty()
        return all_repos

    def get_repo_languages(self, repo_full_name: str) -> Dict:
        return self._make_request(f"repos/{repo_full_name}/languages") or {}

    def get_commit_activity(self, repo_full_name: str) -> List[Dict]:
        return self._make_request(f"repos/{repo_full_name}/stats/commit_activity") or []

    def analyze_user_activity(self, username: str) -> Dict:
        with st.spinner(f"Analyzing GitHub activity for {username}..."):
            user_info = self.get_user_info(username)
            if not user_info:
                return {}

            repositories = self.get_user_repos(username)
            
            analysis = {
                "user_info": {
                    "name": user_info.get("name", "N/A"),
                    "bio": user_info.get("bio", "N/A"),
                    "location": user_info.get("location", "N/A"),
                    "public_repos": user_info.get("public_repos", 0),
                    "followers": user_info.get("followers", 0),
                    "following": user_info.get("following", 0),
                    "created_at": user_info.get("created_at", "N/A"),
                    "avatar_url": user_info.get("avatar_url", "")
                },
                "coding_patterns": {
                    "languages": Counter(),
                    "commit_days": Counter(),
                    "repo_topics": Counter(),
                    "repo_sizes": [],
                },
                "repository_insights": {
                    "total_stars": 0,
                    "total_forks": 0,
                    "popular_repos": [],
                    "recent_activity": []
                }
            }

            for repo in repositories:
                # Language analysis
                languages = self.get_repo_languages(repo["full_name"])
                for language, bytes_count in languages.items():
                    analysis["coding_patterns"]["languages"][language] += bytes_count

                # Commit patterns
                commit_activity = self.get_commit_activity(repo["full_name"])
                if commit_activity:
                    for week in commit_activity:
                        for day_idx, count in enumerate(week.get("days", [])):
                            if count > 0:
                                day_name = calendar.day_abbr[day_idx]
                                analysis["coding_patterns"]["commit_days"][day_name] += count

                # Repository insights
                analysis["repository_insights"]["total_stars"] += repo["stargazers_count"]
                analysis["repository_insights"]["total_forks"] += repo["forks_count"]

                if repo["stargazers_count"] > 0:
                    analysis["repository_insights"]["popular_repos"].append({
                        "name": repo["name"],
                        "stars": repo["stargazers_count"],
                        "forks": repo["forks_count"],
                        "description": repo["description"] or "No description",
                        "main_language": repo["language"] or "Not specified"
                    })

            analysis["repository_insights"]["popular_repos"].sort(
                key=lambda x: x["stars"], reverse=True
            )

            return analysis

def main():
    st.title("🔍 GitHub Profile Analyzer")
    st.write("Analyze any GitHub profile to get insights about their coding patterns and repository statistics.")

    # Sidebar for input
    with st.sidebar:
        st.header("Authentication")
        st.write("To use this tool, you need a GitHub Personal Access Token.")
        st.write("[How to create a token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)")
        token = st.text_input("Enter GitHub Token", type="password")
        username = st.text_input("Enter GitHub Username")
        analyze_button = st.button("Analyze Profile")

    if analyze_button and token and username:
        analyzer = GitHubAnalyzer(token)
        analysis = analyzer.analyze_user_activity(username)

        if analysis:
            # User Profile Section
            col1, col2 = st.columns([1, 2])
            with col1:
                if analysis["user_info"]["avatar_url"]:
                    st.image(analysis["user_info"]["avatar_url"], width=200)
            with col2:
                st.header(analysis["user_info"]["name"])
                st.write(f"📍 Location: {analysis['user_info']['location']}")
                st.write(f"👥 Followers: {analysis['user_info']['followers']} | Following: {analysis['user_info']['following']}")
                st.write(f"📚 Public Repositories: {analysis['user_info']['public_repos']}")
                st.write(f"🎂 Account created: {analysis['user_info']['created_at'][:10]}")

            # Language Analysis
            st.header("📊 Programming Languages")
            languages = analysis["coding_patterns"]["languages"]
            if languages:
                df_languages = pd.DataFrame([
                    {"Language": lang, "Bytes": bytes_count}
                    for lang, bytes_count in languages.items()
                ])
                fig = px.pie(df_languages, values="Bytes", names="Language",
                           title="Language Distribution")
                st.plotly_chart(fig)

            # Commit Patterns
            st.header("📅 Commit Patterns")
            commit_days = analysis["coding_patterns"]["commit_days"]
            if commit_days:
                df_commits = pd.DataFrame([
                    {"Day": day, "Commits": count}
                    for day, count in commit_days.items()
                ])
                fig = px.bar(df_commits, x="Day", y="Commits",
                           title="Commits by Day of Week")
                st.plotly_chart(fig)

            # Popular Repositories
            st.header("⭐ Top Repositories")
            popular_repos = analysis["repository_insights"]["popular_repos"]
            if popular_repos:
                for repo in popular_repos[:3]:
                    with st.expander(f"{repo['name']} ({repo['main_language']})"):
                        st.write(f"⭐ Stars: {repo['stars']}")
                        st.write(f"🔄 Forks: {repo['forks']}")
                        st.write(f"📝 Description: {repo['description']}")

if __name__ == "__main__":
    main()