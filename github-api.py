import requests
import datetime
import time
from typing import Dict, List, Optional
from collections import Counter
from datetime import datetime, timezone
import calendar

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
                print(f"Waiting {wait_seconds:.0f} seconds due to rate limiting...")
                time.sleep(wait_seconds)

        url = f"{self.base_url}/{endpoint}"
        try:
            response = requests.get(url, headers=self.headers, params=params)
            self.rate_limit_remaining = int(response.headers.get('X-RateLimit-Remaining', 0))
            self.rate_limit_reset = int(response.headers.get('X-RateLimit-Reset', 0))
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error {response.status_code} for {url}: {response.text}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None

    def get_user_info(self, username: str) -> Optional[Dict]:
        """Fetches basic information about a GitHub user."""
        return self._make_request(f"users/{username}")

    def get_user_repos(self, username: str) -> List[Dict]:
        """Fetches all repositories for a user."""
        all_repos = []
        page = 1
        
        while True:
            repos_page = self._make_request(
                f"users/{username}/repos",
                params={"page": page, "per_page": 100, "sort": "updated"}
            )
            
            if not repos_page or not isinstance(repos_page, list):
                break
                
            if not repos_page:  # Empty page means we've reached the end
                break
                
            all_repos.extend(repos_page)
            page += 1
            
            print(f"Fetched {len(all_repos)} repositories so far...")
        
        return all_repos

    def get_repo_languages(self, repo_full_name: str) -> Dict:
        """Gets the languages used in a repository and their byte counts."""
        return self._make_request(f"repos/{repo_full_name}/languages") or {}

    def get_commit_activity(self, repo_full_name: str) -> List[Dict]:
        """Analyzes commit patterns for a repository."""
        return self._make_request(f"repos/{repo_full_name}/stats/commit_activity") or []

    def analyze_user_activity(self, username: str) -> Dict:
        """Performs comprehensive analysis of GitHub activity with enhanced metrics."""
        print(f"\nAnalyzing GitHub activity for {username}...")
        
        user_info = self.get_user_info(username)
        if not user_info:
            return {}

        repositories = self.get_user_repos(username)
        
        # Initialize our enhanced analysis structure
        analysis = {
            "user_info": {
                "name": user_info.get("name", "N/A"),
                "bio": user_info.get("bio", "N/A"),
                "location": user_info.get("location", "N/A"),
                "public_repos": user_info.get("public_repos", 0),
                "followers": user_info.get("followers", 0),
                "following": user_info.get("following", 0),
                "created_at": user_info.get("created_at", "N/A")
            },
            "coding_patterns": {
                "languages": Counter(),
                "commit_days": Counter(),
                "repo_topics": Counter(),
                "repo_sizes": [],
                "active_times": []
            },
            "repository_insights": {
                "total_stars": 0,
                "total_forks": 0,
                "popular_repos": [],
                "recent_activity": []
            }
        }

        # Analyze each repository in detail
        for repo in repositories:
            # Get language statistics
            languages = self.get_repo_languages(repo["full_name"])
            for language, bytes_count in languages.items():
                analysis["coding_patterns"]["languages"][language] += bytes_count

            # Analyze commit patterns
            commit_activity = self.get_commit_activity(repo["full_name"])
            if commit_activity:
                for week in commit_activity:
                    for day_idx, count in enumerate(week.get("days", [])):
                        if count > 0:
                            day_name = calendar.day_abbr[day_idx]
                            analysis["coding_patterns"]["commit_days"][day_name] += count

            # Track repository insights
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

        # Sort and format results
        analysis["repository_insights"]["popular_repos"].sort(
            key=lambda x: x["stars"], reverse=True
        )

        return analysis

    def print_enhanced_report(self, analysis: Dict):
        """Prints a detailed, well-formatted analysis report."""
        if not analysis:
            print("No analysis data available.")
            return

        print("\n=== GitHub Profile Analysis ===")
        
        # User Overview
        user = analysis["user_info"]
        print(f"\n👤 User Profile")
        print(f"Name: {user['name']}")
        print(f"Location: {user['location']}")
        print(f"Account created: {user['created_at'][:10]}")
        print(f"Followers: {user['followers']} | Following: {user['following']}")

        # Language Analysis
        print("\n📊 Programming Languages")
        total_bytes = sum(analysis["coding_patterns"]["languages"].values())
        if total_bytes > 0:
            for language, bytes_count in analysis["coding_patterns"]["languages"].most_common(5):
                percentage = (bytes_count / total_bytes) * 100
                print(f"{language}: {percentage:.1f}%")
        else:
            print("No language data available")

        # Commit Patterns
        print("\n📅 Commit Patterns")
        total_commits = sum(analysis["coding_patterns"]["commit_days"].values())
        if total_commits > 0:
            for day, count in analysis["coding_patterns"]["commit_days"].most_common():
                percentage = (count / total_commits) * 100
                print(f"{day}: {percentage:.1f}% ({count} commits)")
        else:
            print("No commit pattern data available")

        # Popular Repositories
        print("\n⭐ Top Repositories")
        if analysis["repository_insights"]["popular_repos"]:
            for repo in analysis["repository_insights"]["popular_repos"][:3]:
                print(f"\n{repo['name']} ({repo['main_language']})")
                print(f"Stars: {repo['stars']} | Forks: {repo['forks']}")
                print(f"Description: {repo['description']}")
        else:
            print("No repository data available")

def main():
    token = input("Enter your GitHub token: ")
    analyzer = GitHubAnalyzer(token)
    username = input("Enter GitHub username to analyze: ")
    
    analysis = analyzer.analyze_user_activity(username)
    analyzer.print_enhanced_report(analysis)

if __name__ == "__main__":
    main()