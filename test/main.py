import argparse
import linkedin_ez as ez
import linkedin_rockapis as rock

def get_parser():
    parser = argparse.ArgumentParser(description='LinkedIn EZ Scraper')
    parser.add_argument('-k', '--keywords', required=True, help='Search keywords')
    parser.add_argument('-l', '--location', required=True, help='Location')
    return parser

def main():
    parser = get_parser()
    args = parser.parse_args()
    # ez.get_jobs(args)
    rock.get_jobs(args)


if __name__ == '__main__':
    main()
