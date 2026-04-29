import requests
import argparse
import json

def lookup_players(name=None, club=None):
    base_url = "http://127.0.0.1:5000/api/stats"
    params = {}
    
    if name:
        params['name'] = name
    if club:
        params['club'] = club
    
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
       
        
        
        for player in data['players']:
            print(f"Tên cầu thủ: {player.get('player', 'N/A')}")
            print(f"Câu lạc bộ:  {player.get('squad', 'N/A')}")
            print(f"Bàn thắng:  {player.get('gls', 'N/A')}")
            print(f"Kiến tạo:   {player.get('ast', 'N/A')}")
            print(f"Trận đấu:   {player.get('mp', 'N/A')}")
            print(f"Quoc Tich: {player.get('nation','N/A')}")
            
  
def main():
    parser = argparse.ArgumentParser(
        description='Tra cứu thông tin cầu thủ Premier League',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''

        '''
    )
    
    parser.add_argument('--name', type=str, help='Tên cầu thủ cần tra cứu')
    parser.add_argument('--club', type=str, help='Tên câu lạc bộ cần tra cứu')
    
    args = parser.parse_args()
    
    if not args.name and not args.club:
        
        lookup_players()
    else:
        lookup_players(name=args.name, club=args.club)

if __name__ == "__main__":
    main()