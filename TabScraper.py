import urllib
import urllib2
import re
import os
import errno

def main():
  artist = raw_input("Enter artist: ")
  output_folder = artist + "/"
  try: 
    os.makedirs(output_folder)
  except OSError as exception:
    if exception.errno != errno.EEXIST:
      raise
  artist = artist.replace(' ', '_')
  
  # Find all the search pages with content
  search_page_contents = []
  search_url_p1 = "http://www.ultimate-guitar.com/tabs/"
  search_url_p2 = "_pro_tabs"
  search_url_p3 = ".htm"
  i = 1
  while True:
    search_page = search_url_p1 + artist + search_url_p2 + str(i) + search_url_p3
    try:
      response = urllib2.urlopen(search_page)
      search_page_contents.append(response.read())
    except:
      break
    i += 1
  print str(len(search_page_contents)) + " pages of tabs found for " + artist
  
  tab_links = {}    # song_name -> list of tab URLs for the song
  for content in search_page_contents:
    link_pattern = r"http://tabs.ultimate-guitar.com/" + artist[0] + "/" + artist + "/(?P<song_name>.*)_guitar_pro.htm"
    song_names = re.findall(link_pattern, content)
    version_pattern = r".*_ver."
    for song_name in song_names:
      if re.match(version_pattern, song_name):
        name_without_version = re.search(r"(?P<name>.*)_ver.", song_name).group('name')
      else:
        name_without_version = song_name
      full_link = "http://tabs.ultimate-guitar.com/" + artist[0] + "/" + artist + "/" + song_name + "_guitar_pro.htm"
      if name_without_version not in tab_links.keys():
        tab_links[name_without_version] = []
      tab_links[name_without_version].append(full_link)
  
  # Find only the best rated version (id + name) of each tab
  print "Finding the best rated version of each tab (this may take some minutes)"
  best_tabs = []
  for song_name in tab_links.keys():
    links = tab_links[song_name]
    best_id = None
    best_rating = 0
    for link in links:
      content = urllib2.urlopen(link).read()
      content = content[content.find("""<div class="raiting">"""):]
      voting_pattern = r"""<div class="raiting">(?P<voting>.*?)</div>"""
      voting = re.search(voting_pattern, content, re.DOTALL).group('voting')
      rating = voting.replace('\n', '').count('class="cur"')
      if rating >= best_rating:
        best_rating = rating
        content = content[content.find("<input type='hidden' name='id'"):]
        dl_link_pattern = r"""<input type='hidden' name='id' value='(?P<song_id>.*)' id="tab_id">"""
        best_id = re.search(dl_link_pattern, content).group('song_id')
    best_tabs.append((best_id, song_name))
  
  print "Best tabs found; downloading tabs..."
  for i in range(len(best_tabs)):
    tab = best_tabs[i]
    id, name = tab[0], tab[1]
    urllib.urlretrieve("http://tabs.ultimate-guitar.com/tabs/download?id=" + id, output_folder + name + ".gp5")
    print str(i+1) + "/" + str(len(best_tabs)) + " " + name
  
  
if __name__ == '__main__':
  main()