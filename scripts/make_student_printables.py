"""Build one original, student-facing reading/craft pack for each shared weekly book."""
import json, math, pathlib, re, datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import HexColor, white
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.utils import ImageReader

ROOT=pathlib.Path(__file__).resolve().parents[1]
DATA=(ROOT/'dist/data.js').read_text()
WEEKS=json.JSONDecoder().raw_decode(DATA.split('const WEEKS=',1)[1])[0]
LESSONS=json.JSONDecoder().raw_decode(DATA.split('const LESSONS=',1)[1])[0]
OUT=ROOT/'dist/resources'
ART_RAW=ROOT/'scripts/art/raw'
ART_CROPS=ROOT/'scripts/art/crops'
W,H=letter

PUR=HexColor('#7145A3'); LAV=HexColor('#F1E9F8'); TEAL=HexColor('#188579'); MINT=HexColor('#E7F5F1')
GOLD=HexColor('#E5A52F'); PALE=HexColor('#FFF3D9'); CORAL=HexColor('#E87759'); PINK=HexColor('#FCE9E4')
BLUE=HexColor('#397EB8'); INK=HexColor('#293654'); MUTED=HexColor('#5D6B83'); LINE=HexColor('#D6DFE9'); PAPER=HexColor('#FFFEFB')
STYLES={
 'body':ParagraphStyle('body',fontName='Helvetica',fontSize=12,leading=16,textColor=INK),
 'small':ParagraphStyle('small',fontName='Helvetica',fontSize=10.5,leading=13.5,textColor=MUTED),
 'center':ParagraphStyle('center',fontName='Helvetica-Bold',fontSize=12,leading=15,alignment=TA_CENTER,textColor=INK),
 'white':ParagraphStyle('white',fontName='Helvetica-Bold',fontSize=13,leading=16,textColor=white),
}

BOOKS={
 1:{'icon':'witch','cards':[('WITCH','witch'),('CAT','cat'),('DOG','dog'),('BIRD','bird'),('FROG','frog'),('DRAGON','dragon'),('BROOM','broom'),('HAT','hat'),('BOW','bow'),('WAND','wand')],
    'events':[('A belonging blows away.','hat'),('A helper finds it and joins the ride.','dog'),('The broom breaks. A dragon is near!','dragon'),('The friends help. A new broom appears.','broom')],
    'craft':'Make a helper collage or build a paper broom with labeled passengers.'},
 2:{'icon':'pumpkin','cards':[('WITCH','witch'),('GHOST','ghost'),('VAMPIRE','vampire'),('MUMMY','mummy'),('BAT','bat'),('PUMPKIN','pumpkin'),('VINE','leaf'),('PULL','broom')],
    'events':[('A giant pumpkin is ready.','pumpkin'),('One helper cannot pull it free.','witch'),('More helpers join the pull.','ghost'),('Together, the group gets the pumpkin.','helper')],
    'craft':'Create a lift-the-pumpkin paper chain showing each helper in order.'},
 3:{'icon':'bowl','cards':[('CAT','cat'),('SQUIRREL','fox'),('DUCK','bird'),('SOUP POT','bowl'),('SPOON','wand'),('PUMPKIN','pumpkin'),('TREE','tree'),('FRIENDS','helper')],
    'events':[('Friends make soup together.','bowl'),('Each friend has a job.','helper'),('A disagreement changes the plan.','problem'),('The friends make a new plan together.','result')],
    'craft':'Make a paper soup bowl with picture ingredients and a three-part problem/solution strip.'},
 4:{'icon':'leaf','cards':[('LEAF MAN','leaf'),('WIND','wind'),('FIELD','place'),('TREE','tree'),('BIRDS','bird'),('LEAF SHAPES','star')],
    'events':[('The wind lifts the leaves.','wind'),('Leaf Man travels over a field.','place'),('The leaf shapes change as he moves.','leaf'),('Where will Leaf Man go next?','question')],
    'craft':'Create a leaf collage character and map the places it visits in order.'},
 5:{'icon':'leaf','cards':[('FRIENDS','helper'),('LEAF','leaf'),('TRAIL','place'),('HILL','tree'),('WOODS','tree'),('HOME','place')],
    'events':[('Friends set out on a leaf hunt.','helper'),('They travel to a new place.','place'),('They find leaves along the way.','leaf'),('The hunt ends and the friends head home.','home')],
    'craft':'Make a route accordion with one leaf picture and location on each panel.'},
 6:{'icon':'fox','cards':[('FLETCHER','fox'),('TREE','tree'),('LEAF','leaf'),('WIND','wind'),('SNOW','snow'),('SURPRISE','star')],
    'events':[('Fletcher notices leaves falling.','leaf'),('He tries to help his tree.','fox'),('The last leaf falls.','wind'),('Fletcher discovers something special.','star')],
    'craft':'Make a tree collage with removable leaves and a three-part change-over-time sequence.'},
 7:{'icon':'tree','cards':[('SPRING','flower'),('SUMMER','sun'),('FALL','leaf'),('WINTER','snow'),('APPLE TREE','tree'),('ARNOLD','child')],
    'events':[('In spring, the tree begins to grow.','flower'),('In summer, the tree changes.','sun'),('In fall, the tree has apples.','apple'),('In winter, the tree rests.','snow')],
    'craft':'Make a four-season tree wheel with large picture labels and a clear seasonal sequence.'},
 8:{'icon':'penguin','cards':[('PENGUIN FAMILY','penguin'),('SNOW','snow'),('COAT','coat'),('BOOTS','boots'),('HOME','place'),('OUTSIDE','snow')],
    'events':[('The family gets ready for winter.','penguin'),('The weather is cold and snowy.','snow'),('One penguin wants to stay home.','home'),('The family finds a way to enjoy the day.','helper')],
    'craft':'Design a winter-weather outfit for a paper penguin and label each clothing choice.'},
 9:{'icon':'snow','cards':[('PETER','child'),('SNOW','snow'),('FOOTPRINTS','footprints'),('SNOWBALL','snowball'),('NEIGHBORHOOD','place'),('MORNING','sun')],
    'events':[('Peter wakes up to snow.','snow'),('He explores his neighborhood.','footprints'),('He makes a snowball and plays.','snowball'),('The next day brings another surprise.','sun')],
    'craft':'Make a layered neighborhood scene with a beginning-middle-end winter walk sequence.'},
}

def para(c,text,x,top,w,style='body',maxh=120):
 q=Paragraph(text,STYLES[style]); _,h=q.wrap(w,maxh); q.drawOn(c,x,top-h); return h
def rounded(c,x,y,w,h,fill=white,stroke=LINE,r=12,dash=False,sw=1):
 c.setLineWidth(sw); c.setStrokeColor(stroke); c.setFillColor(fill)
 if dash:c.setDash(4,3)
 c.roundRect(x,y,w,h,r,fill=1,stroke=1)
 if dash:c.setDash()
def pill(c,text,x,y,fill,fg=INK,w=None):
 w=w or stringWidth(text,'Helvetica-Bold',9)+20
 c.setFillColor(fill); c.roundRect(x,y,w,22,11,fill=1,stroke=0); c.setFillColor(fg); c.setFont('Helvetica-Bold',9); c.drawCentredString(x+w/2,y+7,text)
def line_set(c,x,y,w):
 c.setStrokeColor(HexColor('#9EABC0')); c.setLineWidth(.9); c.line(x,y,x+w,y)
 c.setDash(2,2); c.setStrokeColor(HexColor('#BEC8D6')); c.line(x,y+10,x+w,y+10); c.setDash()
 c.setStrokeColor(HexColor('#9EABC0')); c.line(x,y+20,x+w,y+20)
def draw_star(c,x,y,r):
 pts=[]
 for i in range(10):
  a=math.pi/2+i*math.pi/5; rr=r if i%2==0 else r*.44; pts.append((x+rr*math.cos(a),y+rr*math.sin(a)))
 path=c.beginPath(); path.moveTo(*pts[0])
 for pt in pts[1:]:path.lineTo(*pt)
 path.close(); c.drawPath(path,fill=1,stroke=0)
CURRENT_WEEK=1

def prepare_art_tiles():
 """Check that every book has its prepared, isolated transparent art stickers."""
 missing=[ART_CROPS/f'week-{week}-tile-{idx}.png' for week in range(1,10) for idx in range(9) if not (ART_CROPS/f'week-{week}-tile-{idx}.png').is_file()]
 if not (ART_CROPS/'week-1-bow.png').is_file(): missing.append(ART_CROPS/'week-1-bow.png')
 if missing: raise FileNotFoundError(f'Missing {len(missing)} prepared student art tiles; run scripts/build_art_tiles.py')

def icon(c,kind,cx,cy,size,tile_idx=None):
 """Place the current book's painted story art wherever a student picture cue belongs."""
 if tile_idx is None:
  cards=BOOKS[CURRENT_WEEK]['cards']
  tile_idx=next((i for i,(_,card_kind) in enumerate(cards) if card_kind==kind),None)
  if tile_idx is None:
   # Story-structure cues borrow a character or scene from this week's shared book.
   fallback={'place':1,'question':2,'first':0,'next':1,'last':2,'problem':1,'helper':2,'result':3,'book':0,'star':4,'sun':2,'flower':1,'snow':4,'wind':2,'tree':1,'home':2,'apple':5,'child':0,'coat':3,'boots':4,'footprints':2}
   tile_idx=fallback.get(kind,0)
  tile_idx=min(tile_idx,8)
 path=ART_CROPS/'week-1-bow.png' if CURRENT_WEEK==1 and kind=='bow' else ART_CROPS/f'week-{CURRENT_WEEK}-tile-{tile_idx}.png'
 c.drawImage(ImageReader(str(path)),cx-size/2,cy-size/2,size,size,mask='auto',preserveAspectRatio=True,anchor='c')

def header(c,w,lesson,title,accent):
 c.setFillColor(PAPER); c.rect(0,0,W,H,fill=1,stroke=0)
 c.setFillColor(accent); c.roundRect(38,H-66,5,29,2,fill=1,stroke=0)
 date=datetime.date.fromisoformat(lesson['date']).strftime('%A, %B %d').replace(' 0',' '); c.setFillColor(accent); c.setFont('Helvetica-Bold',10); c.drawString(52,H-48,f"WEEK {w['n']}  •  {date}")
 c.setFillColor(INK); c.setFont('Helvetica-Bold',23); c.drawString(39,H-91,title[:43])
 c.setFillColor(MUTED); c.setFont('Helvetica-Bold',8.5); c.drawString(40,H-116,w['books3'].upper())
 icon(c,BOOKS[w['n']]['icon'],W-85,H-77,68)
def footer(c,page,w):
 c.setStrokeColor(LINE); c.line(38,38,W-38,38); c.setFillColor(MUTED); c.setFont('Helvetica',8)
 c.drawString(40,23,'READ • LOOK • MATCH • TELL • CREATE'); c.drawRightString(W-40,23,f"WEEK {w['n']}  •  {page}")

def page_wh(c,w,l,num,accent):
 header(c,w,l,'Look in the book and find',accent)
 para(c,'Point to a picture. Match a card. Tell, draw, or write your answer.',40,635,W-80)
 prompts=[('WHO?','Who or what is on this page?','witch'),('WHERE / WHEN?','Where is it? When is this happening?','place'),('WHAT?','What happens or what do you notice?','question')]
 for i,(lab,q,kind) in enumerate(prompts):
  y=445-i*127; fill=[LAV,MINT,PALE][i]; acc=[PUR,TEAL,GOLD][i]
  rounded(c,40,y,532,109,white,acc,14,sw=1.2); icon(c,kind,92,y+57,67)
  c.setFillColor(acc); c.setFont('Helvetica-Bold',14); c.drawString(140,y+77,lab)
  para(c,q,140,y+62,395,'small',26)
  c.setStrokeColor(LINE); c.roundRect(140,y+13,410,34,8,fill=0,stroke=1); c.setFillColor(MUTED); c.setFont('Helvetica',9); c.drawString(151,y+25,'My answer / picture clue')
 pill(c,'POINT',43,54,LAV,PUR,82); pill(c,'MATCH',135,54,MINT,TEAL,82); pill(c,'TELL / AAC',227,54,PALE,INK,94); pill(c,'DRAW / WRITE',331,54,PINK,CORAL,116)
 footer(c,num,w)

def page_sequence(c,w,num,accent):
 header(c,w,LESSONS_BY_WEEK[w['n']][1],'Put the story in order',accent)
 para(c,'Cut the event cards below. Put them in order. Tell what happened first, next, and last.',40,635,W-80)
 for i,(lab,fill,acc,kind) in enumerate([('FIRST',LAV,PUR,'first'),('NEXT',MINT,TEAL,'next'),('THEN',PALE,GOLD,'helper'),('LAST',PINK,CORAL,'last')]):
  x=40+i*135; y=435; rounded(c,x,y,122,160,white,acc,13,sw=1.2); pill(c,lab,x+16,y+131,fill,acc,90)
  c.setStrokeColor(LINE); c.setDash(3,3); c.roundRect(x+17,y+42,88,74,9,fill=0,stroke=1); c.setDash(); icon(c,kind,x+61,y+80,47)
  c.setFillColor(MUTED); c.setFont('Helvetica',8); c.drawCentredString(x+61,y+25,'glue a story card')
 events=BOOKS[w['n']]['events']
 for i,(text,kind) in enumerate(events):
  col=i%2; row=i//2; x=40+col*272; y=238-row*83
  rounded(c,x,y,260,69,[LAV,MINT,PINK,PALE][i],[PUR,TEAL,CORAL,GOLD][i],11,dash=True)
  icon(c,kind,x+37,y+35,48); para(c,text,x+70,y+52,174,'small',43)
  c.setFillColor(MUTED); c.setFont('Helvetica-Bold',7.5); c.drawRightString(x+249,y+7,'CUT')
 footer(c,num,w)

def page_bme(c,w,l,num,accent):
 header(c,w,l,'Beginning • Middle • End',accent)
 para(c,'Draw or place a page picture. Then tell or write what happens.',40,635,W-80)
 for i,(label,q,fill,acc) in enumerate([('BEGINNING','Who is here? Where does it start?',LAV,PUR),('MIDDLE','What happens? Who helps or what changes?',MINT,TEAL),('END','How does this part end?',PALE,GOLD)]):
  y=389-i*112; rounded(c,40,y,532,98,white,acc,14,sw=1.2); c.setFillColor(fill); c.roundRect(54,y+57,130,27,10,fill=1,stroke=0)
  c.setFillColor(acc); c.setFont('Helvetica-Bold',10.5); c.drawCentredString(119,y+66,label); para(c,q,200,y+79,350,'small',28)
  c.setStrokeColor(LINE); c.roundRect(55,y+12,129,38,7,fill=0,stroke=1); c.setFillColor(MUTED); c.setFont('Helvetica',8); c.drawCentredString(119,y+27,'DRAW / PICTURE')
  line_set(c,200,y+19,350)
 footer(c,num,w)

def page_cause(c,w,l,num,accent):
 header(c,w,l,'What happened because?',accent)
 para(c,'Look at a page. Show what happened, what a character did, and what changed.',40,635,W-80)
 for i,(lab,q,kind,fill,acc) in enumerate([('THE PROBLEM','What went wrong?','problem',PINK,CORAL),('A HELPER ACTED','What did someone do?','helper',MINT,TEAL),('THE RESULT','What happened after?','result',PALE,GOLD)]):
  x=40+i*180; rounded(c,x,344,164,218,white,acc,14,sw=1.2); pill(c,lab,x+12,528,fill,acc,140); icon(c,kind,x+82,480,70)
  para(c,q,x+14,430,136,'center',40); c.setStrokeColor(LINE); c.setDash(3,3); c.roundRect(x+16,371,132,43,8,fill=0,stroke=1); c.setDash()
  c.setFillColor(MUTED); c.setFont('Helvetica',7.6); c.drawCentredString(x+82,360,'DRAW / ADD BOOK CLUE')
  if i<2:c.setStrokeColor(GOLD); c.setLineWidth(2); c.line(x+164,455,x+176,455); c.line(x+170,461,x+176,455); c.line(x+170,449,x+176,455)
 rounded(c,40,218,532,95,HexColor('#F7F8FA'),LINE,13); c.setFillColor(INK); c.setFont('Helvetica-Bold',12); c.drawString(57,288,'MY STORY ANSWER')
 para(c,'The problem was ____________. The helper ____________. Then ____________.',57,270,492,'small',24); line_set(c,57,232,490)
 rounded(c,40,75,532,120,HexColor('#FFF9EE'),HexColor('#F0DDAF'),13); c.setFillColor(INK); c.setFont('Helvetica-Bold',11); c.drawString(57,173,'SHOW THE BOOK CLUE')
 para(c,'Draw the picture or mark the page that helped you answer.',57,157,480,'small',22)
 c.setStrokeColor(LINE); c.setDash(4,3); c.roundRect(57,89,207,48,8,fill=0,stroke=1); c.setDash(); c.setFont('Helvetica',8); c.setFillColor(MUTED); c.drawCentredString(160,78,'PICTURE CLUE')
 c.setFillColor(INK); c.setFont('Helvetica',9); c.drawString(285,125,'Page: _________'); line_set(c,285,98,253)
 footer(c,num,w)

def page_info(c,w,l,num,accent,kind):
 header(c,w,l,'What does this book teach?',accent)
 para(c,'Look closely at the pictures and words. Find a detail that teaches you something.',40,635,W-80)
 titles= [('TOPIC','What is this book mostly about?','book',LAV,PUR),('DETAIL','What do you learn on this page?','question',MINT,TEAL),('EVIDENCE','Show the picture or words that teach you.','star',PALE,GOLD)]
 for i,(lab,q,k,fill,acc) in enumerate(titles):
  y=432-i*132; rounded(c,40,y,532,112,white,acc,14,sw=1.2); icon(c,k,93,y+60,68); c.setFillColor(acc); c.setFont('Helvetica-Bold',14); c.drawString(140,y+81,lab)
  para(c,q,140,y+65,390,'small',28); c.setStrokeColor(LINE); c.roundRect(140,y+14,410,35,8,fill=0,stroke=1); c.setFillColor(MUTED); c.setFont('Helvetica',9); c.drawString(151,y+26,'Draw / write a detail')
 pill(c,'POINT TO THE PAGE',45,54,LAV,PUR,142); pill(c,'TELL / AAC',201,54,MINT,TEAL,110); pill(c,'DRAW / WRITE',325,54,PALE,INK,118)
 footer(c,num,w)

def page_season(c,w,l,num,accent,compare=False):
 header(c,w,l,'Compare the seasons' if compare else 'A tree changes through the year',accent)
 para(c,'Look at two season pages. Draw what changes. Find a detail in the book.',40,635,W-80)
 seasons=[('SPRING','flower',PINK,CORAL),('SUMMER','sun',PALE,GOLD),('FALL','leaf',MINT,TEAL),('WINTER','snow',HexColor('#E8F1F9'),BLUE)]
 for i,(lab,k,fill,acc) in enumerate(seasons):
  col=i%2; row=i//2; x=40+col*272; y=379-row*151
  rounded(c,x,y,260,132,white,acc,14,sw=1.2); pill(c,lab,x+15,y+98,fill,acc,93); icon(c,k,x+214,y+100,49)
  c.setStrokeColor(LINE); c.roundRect(x+16,y+14,228,65,8,fill=0,stroke=1); c.setFillColor(MUTED); c.setFont('Helvetica',8); c.drawCentredString(x+130,y+4,'DRAW A DETAIL / WRITE A CLUE')
 rounded(c,40,71,532,119,HexColor('#F7F8FA'),LINE,12); c.setFillColor(INK); c.setFont('Helvetica-Bold',12); c.drawString(56,167,'TWO-SEASON THINKING')
 para(c,'In __________, the tree __________. In __________, the tree __________.',56,148,490,'small',28); line_set(c,56,98,490)
 footer(c,num,w)

def page_friday(c,w,l,num,accent,informational=False):
 header(c,w,l,'Show what you know',accent)
 para(c,'Find your answers in the book. Point, match, tell, draw, or write.',40,635,W-80)
 if informational:
  prompts=[('1','What is this book mostly about?'),('2','Name or show one detail you learned.'),('3','How does that detail teach about the topic?')]
 else:
  prompts=[('1','Who or what is in this part?'),('2','What happened first, next, or last?'),('3','What changed? Show a page clue.')]
 for i,(n,q) in enumerate(prompts):
  y=439-i*113; rounded(c,40,y,532,94,[LAV,MINT,PALE][i],[PUR,TEAL,GOLD][i],13,sw=1.1)
  c.setFillColor([PUR,TEAL,GOLD][i]); c.circle(73,y+55,17,fill=1,stroke=0); c.setFillColor(white); c.setFont('Helvetica-Bold',11); c.drawCentredString(73,y+51,n)
  para(c,q,105,y+70,435,'body',27); line_set(c,105,y+31,435)
 rounded(c,40,78,532,76,HexColor('#FFF9EE'),HexColor('#F0DDAF'),12); c.setFillColor(INK); c.setFont('Helvetica-Bold',11); c.drawString(56,134,'MY BOOK CLUE / DRAWING')
 c.setStrokeColor(LINE); c.setDash(3,3); c.roundRect(57,89,497,31,7,fill=0,stroke=1); c.setDash()
 footer(c,num,w)

def page_craft(c,w,num,accent):
 title=BOOKS[w['n']]['craft']
 prompt=re.sub(r'^(Make|Create|Design)\s+','',title.strip())
 header(c,w,LESSONS_BY_WEEK[w['n']][1],'Make a book-inspired creation!',accent)
 para(c,prompt[0].upper()+prompt[1:]+' Color your design. Add labels or a story clue.',40,635,W-80)
 # playful theme stamp and a large open design surface
 rounded(c,40,196,532,397,HexColor('#FBF7FF'),HexColor('#DCCDEB'),16,sw=1.2)
 c.setFillColor(PUR); c.setFont('Helvetica-Bold',13); c.drawString(58,566,'MY PLAN')
 para(c,'I will make __________________________.',58,548,470,'body',27); line_set(c,58,509,470)
 c.setFillColor(PUR); c.setFont('Helvetica-Bold',13); c.drawString(58,478,'MY PICTURE / CRAFT')
 c.setStrokeColor(HexColor('#BFCADB')); c.setDash(5,4); c.roundRect(58,239,496,220,12,fill=0,stroke=1); c.setDash()
 craft_art='broom' if w['n']==1 else BOOKS[w['n']]['icon']
 icon(c,craft_art,W/2,352,112)
 c.setFillColor(MUTED); c.setFont('Helvetica',9); c.drawCentredString(W/2,219,'DRAW IT HERE • ADD YOUR OWN DETAILS')
 # cut-out tokens for assembling the finished work
 labels=BOOKS[w['n']]['cards'][:3]
 for i,(label,k) in enumerate(labels):
  x=57+i*174; rounded(c,x,86,154,93,white,[PUR,TEAL,GOLD][i],10,dash=True); icon(c,k,x+42,132,54)
  c.setFillColor(INK); c.setFont('Helvetica-Bold',8.5); c.drawCentredString(x+106,134,label[:14])
  c.setFillColor(MUTED); c.setFont('Helvetica',7.5); c.drawCentredString(x+106,117,'CUT OUT')
 footer(c,num,w)

def day_kind(lesson,day_index,total,week_n):
 skill=lesson['subjects'][0]['targets']['g3']['skill'].lower()
 if week_n==7:
  if 'compare' in skill or 'place three seasonal' in skill or 'how or why' in skill:return 'season_compare'
  if 'season' in skill:return 'season'
  if day_index==total-1:return 'friday'
  if 'topic' in skill:return 'information'
 if day_index==total-1:return 'friday'
 if 'who and where' in skill:return 'wh'
 if 'what happened next' in skill or 'sequence' in skill or 'retell the event sequence' in skill:return 'sequence'
 if 'beginning, middle and end' in skill:return 'bme'
 if 'why or how' in skill:return 'cause'
 return 'wh'

LESSONS_BY_WEEK={w['n']:sorted([l for l in LESSONS if l['week']==w['n']],key=lambda l:l['date']) for w in WEEKS}
ACCENTS=[PUR,CORAL,TEAL,GOLD,BLUE,PUR,TEAL,BLUE,CORAL]
OUT.mkdir(parents=True,exist_ok=True)
prepare_art_tiles()
for w in WEEKS:
 n=w['n']; CURRENT_WEEK=n; lessons=LESSONS_BY_WEEK[n]; book=w['books3']; assert book==w['books4'],f'Week {n}: shared books diverge'
 bookdata=BOOKS[n]; path=OUT/f'week-{n}-student-printables.pdf'
 pdf=canvas.Canvas(str(path),pagesize=letter)
 pdf.setTitle(f'Week {n} student printables • {book}'); pdf.setAuthor('Stacie Classroom')
 # Start directly with the student work; the weekly art and layout stay consistent.
 page_num=1
 for di,l in enumerate(lessons):
  typ=day_kind(l,di,len(lessons),n); ac=ACCENTS[(n+di-1)%len(ACCENTS)]
  if typ=='wh':page_wh(pdf,w,l,page_num,ac)
  elif typ=='sequence':page_sequence(pdf,w,page_num,ac)
  elif typ=='bme':page_bme(pdf,w,l,page_num,ac)
  elif typ=='cause':page_cause(pdf,w,l,page_num,ac)
  elif typ=='information':page_info(pdf,w,l,page_num,ac,typ)
  elif typ in ('season','season_compare'):page_season(pdf,w,l,page_num,ac,typ=='season_compare')
  else:page_friday(pdf,w,l,page_num,ac,n==7)
  pdf.showPage(); page_num+=1
  if di==0:
   # Place the book-specific cut-apart visual cards after the first response page.
   pdf.setFillColor(PAPER); pdf.rect(0,0,W,H,fill=1,stroke=0); pdf.setFillColor(INK); pdf.setFont('Helvetica-Bold',22); pdf.drawString(40,H-51,'Cut-apart picture cards')
   para(pdf,'Cut on the dotted lines. Match the pictures to your book. Use them to show what happened.',40,H-68,W-80)
   cards=bookdata['cards']; cw=250; ch=99; gapx=22; gapy=12; x0=45; ytop=H-128
   for i,(label,k) in enumerate(cards):
    col=i%2; row=i//2; x=x0+col*(cw+gapx); y=ytop-(row+1)*ch-row*gapy
    rounded(pdf,x,y,cw,ch,[LAV,MINT,PALE,PINK,HexColor('#E8F1F9')][i%5],[PUR,TEAL,GOLD,CORAL,BLUE][i%5],12,dash=True); icon(pdf,k,x+54,y+50,63,tile_idx=min(i,8))
    pdf.setFillColor(INK); pdf.setFont('Helvetica-Bold',13); pdf.drawString(x+105,y+45,label[:19])
   pdf.showPage(); page_num+=1
 # Craft/activity page is student-facing; no teacher procedure block.
 page_craft(pdf,w,page_num,ACCENTS[n-1]); pdf.showPage(); pdf.save()
 print(path.name,book, f'{page_num} pages')
