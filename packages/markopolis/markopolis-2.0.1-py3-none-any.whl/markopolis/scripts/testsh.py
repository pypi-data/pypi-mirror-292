import sh
import re
import fire
from markopolis.config import settings
import os

MDROOT = settings.md_path


def main():
    fire.Fire()

def find_backlinks(target_file):
    pth = settings.md_path
    print(f"Searching for backlinks to: {target_file}")
    print(f"In vault directory: {pth}")


    # The pattern for backlinks in the markdown format [[<filename>]]
    target = target_file.split(".")[0]
    backlink_pattern = fr"\[\[{re.escape(target)}\]\]"

    try:
        # Use sh.Command to get the full path of rg
        rg = sh.Command("rg")

        # Run ripgrep to search for backlinks
        result = rg("-l", backlink_pattern, pth, _err_to_out=True)

        if result:
            matches = result.splitlines()

            for match in matches:
                print(match)
        else:
            print("No backlinks found.")

    except sh.CommandNotFound:
        print(
            "Error: ripgrep (rg) command not found. Make sure it's installed and in your PATH."
        )
    except sh.ErrorReturnCode as e:
        print(f"ripgrep command failed with exit code {e.exit_code}")
        print("STDOUT:")
        print(e.stdout.decode())
        print("STDERR:")
        print(e.stderr.decode())
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        print(f"Error type: {type(e)}")

def search(pattern):
    pth = settings.md_path
    print(f"Searching for pattern: {pattern}")
    print(f"In directory: {pth}")

    try:
        # Use sh.Command to get the full path of rg
        rg = sh.Command("rg")
        print(f"Using ripgrep at: {rg}")

        # Run ripgrep with verbose output
        # result = rg("-l", pattern, pth, _err_to_out=True)
        result = rg("-l", pattern, pth, _err_to_out=True)
        if result is not None:
            matches = result.splitlines()
            print(matches)

            path_pattern = r"(\/[^\s\x1b]+|[a-zA-Z]:\\[^\s\x1b]+)"

            # Find all matching paths using the regex
            paths = [re.findall(path_pattern, input_string) for input_string in matches]
            print(paths)

            for p in paths:
                os.remove(p[0])
        print("Search Results:")
        print(result)
    except sh.CommandNotFound:
        print(
            "Error: ripgrep (rg) command not found. Make sure it's installed and in your PATH."
        )
    except sh.ErrorReturnCode as e:
        print(f"ripgrep command failed with exit code {e.exit_code}")
        print("STDOUT:")
        print(e.stdout.decode())
        print("STDERR:")
        print(e.stderr.decode())
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        print(f"Error type: {type(e)}")


if __name__ == "__main__":
    main()
