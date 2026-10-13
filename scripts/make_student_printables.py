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
 'body':ParagraphStyle('body',fontName='Helvetica',fontSize=15,leading=19,textColor=INK),
 'small':ParagraphStyle('small',fontName='Helvetica',fontSize=13,leading=16.5,textColor=MUTED),
 'center':ParagraphStyle('center',fontName='Helvetica-Bold',fontSize=13.5,leading=17,alignment=TA_CENTER,textColor=INK),
 'white':ParagraphStyle('white',fontName='Helvetica-Bold',fontSize=13,leading=16,textColor=white),
 'display':ParagraphStyle('display',fontName='Helvetica-Bold',fontSize=24,leading=29,textColor=white),
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

# Original, student-facing center activities. These are inspired by the kinds of
# choices shown in Stacie's examples, but use original wording and our own art.
RHYMES={
 1:[('BROOM','ROOM','CAT'),('CAT','HAT','DOG'),('FROG','DOG','SUN')],
 2:[('BIG','PIG','SUN'),('VINE','LINE','HAT'),('PULL','FULL','TREE')],
 3:[('POT','HOT','SOUP'),('SPOON','MOON','CAT'),('TREE','BEE','PUMPKIN')],
 4:[('WIND','FIND','LEAF'),('TREE','BEE','WIND'),('FALL','BALL','LEAF')],
 5:[('TREE','BEE','LEAF'),('FALL','BALL','HUNT'),('HILL','WILL','TREE')],
 6:[('FOX','BOX','LEAF'),('TREE','BEE','FOX'),('FELL','SMELL','TREE')],
 7:[('TREE','BEE','APPLE'),('SUN','FUN','TREE'),('FALL','BALL','SUN')],
 8:[('SNOW','GO','BOOT'),('BOOT','HOOT','COLD'),('COLD','OLD','SNOW')],
 9:[('DAY','PLAY','SNOW'),('SNOW','GO','DAY'),('FEET','STREET','SNOW')],
}

# Pick the book-picture tile that best matches the printed rhyme prompt.
RHYME_ART={
 1:[6,1,4], 2:[5,6,7], 3:[3,4,6], 4:[1,3,0], 5:[3,1,3],
 6:[0,1,2], 7:[4,1,2], 8:[1,3,1], 9:[5,2,1],
}

DRAWING={1:('BROOM','broom'),2:('PUMPKIN','pumpkin'),3:('SOUP POT','bowl'),
 4:('A LEAF','leaf'),5:('A LEAF','leaf'),6:('A TREE','tree'),
 7:('AN APPLE TREE','appletree'),8:('A PENGUIN','penguin'),9:('SNOW TRACKS','footprints')}

MASKS={
 1:['......','...##.','...##.','...##.','######','######'],
 2:['..##..','.####.','######','######','.####.','...##.'],
 3:['......','######','######','.####.','..##..','......'],
 4:['...#..','..###.','.#####','####.#','.#####','..###.'],
 5:['..##..','.####.','######','######','.####.','...##.'],
 6:['...##.','..####','.#####','######','.#####','...##.'],
 7:['...##.','..####','.#####','######','.#####','...##.'],
 8:['..##..','.####.','######','######','.####.','.####.'],
 9:['..##..','..##..','.####.','######','.####.','..##..'],
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
def line_set(c,x,y,w,spacing=26):
 """Draw one roomy primary-writing line: solid baselines with a dashed midline."""
 c.setStrokeColor(HexColor('#9EABC0')); c.setLineWidth(1.1); c.line(x,y,x+w,y)
 c.setDash(3,3); c.setStrokeColor(HexColor('#BEC8D6')); c.line(x,y+spacing/2,x+w,y+spacing/2); c.setDash()
 c.setStrokeColor(HexColor('#9EABC0')); c.line(x,y+spacing,x+w,y+spacing)

def writing_rows(c,x,y,w,count=2,spacing=26,gap=10):
 """Draw large primary-writing guides, stacked with a generous baseline-to-baseline gap."""
 for i in range(count): line_set(c,x,y+i*(spacing+gap),w,spacing)

def response_box(c,x,y,w,h,label='DRAW, PLACE A PICTURE, OR WRITE'):
 rounded(c,x,y,w,h,HexColor('#FFFEFC'),LINE,9,dash=True,sw=1.1)
 c.setFillColor(MUTED); c.setFont('Helvetica-Bold',10); c.drawString(x+11,y+h-17,label)
 if h>=80:
  writing_rows(c,x+12,y+6,w-24,2,spacing=24,gap=7)
 elif h>=60:
  writing_rows(c,x+12,y+7,w-24,1,spacing=22,gap=5)
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
 c.setFillColor(MUTED); c.setFont('Helvetica-Bold',9); c.drawString(40,H-116,w['books3'].upper())
 icon(c,BOOKS[w['n']]['icon'],W-83,H-77,74)
def footer(c,page,w):
 c.setStrokeColor(LINE); c.line(38,38,W-38,38); c.setFillColor(MUTED); c.setFont('Helvetica',8)
 c.drawString(40,23,'READ • LOOK • MATCH • TELL • CREATE'); c.drawRightString(W-40,23,f"WEEK {w['n']}  •  {page}")

def page_wh(c,w,l,num,accent):
 header(c,w,l,'Look in the book and find',accent)
 para(c,'Point to a picture. Match a card. Tell, draw, or write your answer.',40,635,W-80,'body',30)
 prompts=[('WHO?','Who or what is on this page?','witch'),('WHERE / WHEN?','Where is it? When is this happening?','place'),('WHAT?','What happens or what do you notice?','question')]
 for i,(lab,q,kind) in enumerate(prompts):
  y=444-i*176; fill=[LAV,MINT,PALE][i]; acc=[PUR,TEAL,GOLD][i]
  rounded(c,40,y,532,164,white,acc,16,sw=1.4); icon(c,kind,93,y+87,83)
  c.setFillColor(acc); c.setFont('Helvetica-Bold',17); c.drawString(151,y+137,lab)
  para(c,q,151,y+115,390,'body',42)
  response_box(c,151,y+12,400,84,'DRAW A CLUE, PLACE A PICTURE, OR WRITE')
 footer(c,num,w)

def page_sequence(c,w,num,accent):
 header(c,w,LESSONS_BY_WEEK[w['n']][0],'Put the story in order',accent)
 para(c,'Put the scenes in order. Cut out the story cards below to help retell.',40,635,W-80,'body',30)
 for i,(lab,fill,acc,kind) in enumerate([('FIRST',LAV,PUR,'first'),('NEXT',MINT,TEAL,'next'),('THEN',PALE,GOLD,'helper'),('LAST',PINK,CORAL,'last')]):
  x=40+i*135; y=402; rounded(c,x,y,122,207,white,acc,14,sw=1.25); pill(c,lab,x+14,y+174,fill,acc,94)
  c.setStrokeColor(LINE); c.setDash(4,3); c.roundRect(x+12,y+48,98,111,9,fill=0,stroke=1); c.setDash(); icon(c,kind,x+61,y+103,61)
  c.setFillColor(MUTED); c.setFont('Helvetica-Bold',8); c.drawCentredString(x+61,y+31,'DRAW / PLACE')
 events=BOOKS[w['n']]['events']
 for i,(text,kind) in enumerate(events):
  col=i%2; row=i//2; x=40+col*272; y=260-row*128
  rounded(c,x,y,260,112,[LAV,MINT,PINK,PALE][i],[PUR,TEAL,CORAL,GOLD][i],12,dash=True,sw=1.3)
  icon(c,kind,x+47,y+58,66); para(c,text,x+91,y+91,153,'small',67)
  c.setFillColor(MUTED); c.setFont('Helvetica-Bold',8); c.drawRightString(x+248,y+8,'CUT OUT')
 footer(c,num,w)

def page_bme(c,w,l,num,accent):
 header(c,w,l,'Beginning • Middle • End',accent)
 para(c,'Draw or place a page picture. Then tell or write what happens.',40,635,W-80,'body',30)
 for i,(label,q,fill,acc) in enumerate([('BEGINNING','Who is here? Where does it start?',LAV,PUR),('MIDDLE','What happens? Who helps or what changes?',MINT,TEAL),('END','How does this part end?',PALE,GOLD)]):
  y=444-i*176; rounded(c,40,y,532,164,white,acc,15,sw=1.3)
  pill(c,label,55,y+132,fill,acc,134); icon(c,['first','helper','last'][i],520,y+141,48)
  para(c,q,55,y+115,425,'body',40)
  response_box(c,55,y+8,497,84,'DRAW THE SCENE, PLACE A CARD, OR WRITE WHAT HAPPENED')
 footer(c,num,w)

def page_cause(c,w,l,num,accent):
 header(c,w,l,'What happened because?',accent)
 para(c,'Look at the pages. Show the problem, what a character did, and what changed.',40,635,W-80,'body',30)
 for i,(lab,q,kind,fill,acc) in enumerate([('THE PROBLEM','What went wrong?','problem',PINK,CORAL),('A HELPER ACTED','What did someone do?','helper',MINT,TEAL),('THE RESULT','What happened after?','result',PALE,GOLD)]):
  y=444-i*176; rounded(c,40,y,532,164,white,acc,15,sw=1.3); pill(c,lab,55,y+132,fill,acc,150)
  icon(c,kind,520,y+141,48); para(c,q,55,y+115,425,'body',40)
  response_box(c,55,y+8,497,84,'DRAW THE BOOK CLUE, PLACE A PICTURE, OR WRITE')
  if i<2:
   c.setFillColor(GOLD); pth=c.beginPath(); pth.moveTo(W/2-6,y-4); pth.lineTo(W/2+6,y-4); pth.lineTo(W/2,y-10); pth.close(); c.drawPath(pth,fill=1,stroke=0)
 footer(c,num,w)

def page_info(c,w,l,num,accent,kind):
 header(c,w,l,'What does this book teach?',accent)
 para(c,'Look closely at the pictures and words. Find a detail that teaches you something.',40,635,W-80,'body',30)
 titles= [('TOPIC','What is this book mostly about?','book',LAV,PUR),('DETAIL','What do you learn on this page?','question',MINT,TEAL),('EVIDENCE','Show the picture or words that teach you.','star',PALE,GOLD)]
 for i,(lab,q,k,fill,acc) in enumerate(titles):
  y=444-i*176; rounded(c,40,y,532,164,white,acc,15,sw=1.3); icon(c,k,94,y+87,83); c.setFillColor(acc); c.setFont('Helvetica-Bold',17); c.drawString(151,y+137,lab)
  para(c,q,151,y+115,390,'body',42); response_box(c,151,y+12,400,84,'DRAW A DETAIL, PLACE A PICTURE, OR WRITE')
 footer(c,num,w)

def page_season(c,w,l,num,accent,compare=False):
 header(c,w,l,'Compare the seasons' if compare else 'A tree changes through the year',accent)
 para(c,'Look at the season pictures. Draw what changes. Find a detail in the book.',40,635,W-80,'body',30)
 seasons=[('SPRING','flower',PINK,CORAL),('SUMMER','sun',PALE,GOLD),('FALL','leaf',MINT,TEAL),('WINTER','snow',HexColor('#E8F1F9'),BLUE)]
 for i,(lab,k,fill,acc) in enumerate(seasons):
  col=i%2; row=i//2; x=40+col*272; y=354-row*250
  rounded(c,x,y,260,235,white,acc,15,sw=1.25); pill(c,lab,x+14,y+200,fill,acc,105); icon(c,k,x+221,y+204,60)
  c.setStrokeColor(LINE); c.setDash(4,3); c.roundRect(x+14,y+72,232,111,9,fill=0,stroke=1); c.setDash()
  c.setFillColor(MUTED); c.setFont('Helvetica-Bold',9.5); c.drawString(x+22,y+166,'DRAW A PAGE CLUE')
  writing_rows(c,x+19,y+13,220,2,spacing=22,gap=6)
 footer(c,num,w)

def page_friday(c,w,l,num,accent,informational=False):
 header(c,w,l,'Show what you know',accent)
 para(c,'Find your answers in the book. Point, match, tell, draw, or write.',40,635,W-80,'body',30)
 if informational:
  prompts=[('1','What is this book mostly about?'),('2','Name or show one detail you learned.'),('3','How does that detail teach about the topic?')]
 else:
  prompts=[('1','Who or what is in this part?'),('2','What happened first, next, or last?'),('3','What changed? Show a page clue.')]
 for i,(n,q) in enumerate(prompts):
  y=444-i*176; rounded(c,40,y,532,164,[LAV,MINT,PALE][i],[PUR,TEAL,GOLD][i],15,sw=1.3)
  c.setFillColor([PUR,TEAL,GOLD][i]); c.circle(75,y+125,21,fill=1,stroke=0); c.setFillColor(white); c.setFont('Helvetica-Bold',14); c.drawCentredString(75,y+120,n)
  para(c,q,112,y+143,420,'body',40)
  response_box(c,57,y+12,497,84,'DRAW, PLACE A PICTURE, OR WRITE YOUR ANSWER')
 footer(c,num,w)

def page_craft(c,w,num,accent):
 title=BOOKS[w['n']]['craft']
 prompt=re.sub(r'^(Make|Create|Design)\s+','',title.strip())
 header(c,w,LESSONS_BY_WEEK[w['n']][0],'Make a book-inspired creation!',accent)
 para(c,prompt[0].upper()+prompt[1:]+' Add story details and labels.',40,635,W-80,'small',38)
 # Full-page planning and creation workspace, followed by large book-art cutouts.
 rounded(c,40,150,532,440,HexColor('#FBF7FF'),HexColor('#DCCDEB'),16,sw=1.3)
 c.setFillColor(PUR); c.setFont('Helvetica-Bold',14); c.drawString(58,559,'MY CRAFT PLAN')
 c.setFillColor(INK); c.setFont('Helvetica-Bold',13); c.drawString(58,520,'I WILL MAKE:')
 writing_rows(c,159,506,394,1,spacing=24,gap=6)
 c.setFillColor(PUR); c.setFont('Helvetica-Bold',14); c.drawString(58,472,'MY BIG PICTURE / CRAFT DESIGN')
 c.setStrokeColor(HexColor('#BFCADB')); c.setLineWidth(1.2); c.setDash(5,4); c.roundRect(58,194,496,267,12,fill=0,stroke=1); c.setDash()
 craft_art='broom' if w['n']==1 else BOOKS[w['n']]['icon']
 icon(c,craft_art,520,432,54)
 c.setFillColor(MUTED); c.setFont('Helvetica-Bold',9); c.drawCentredString(W/2,174,'DRAW LARGE • ADD DETAILS • LABEL YOUR WORK')
 # Cut-out story pieces use the same painted, book-matched illustrations.
 labels=BOOKS[w['n']]['cards'][:3]
 for i,(label,k) in enumerate(labels):
  x=40+i*181; rounded(c,x,60,170,100,white,[PUR,TEAL,GOLD][i],11,dash=True,sw=1.2); icon(c,k,x+50,110,64)
  c.setFillColor(INK); c.setFont('Helvetica-Bold',10.5); c.drawCentredString(x+116,115,label[:14])
  c.setFillColor(MUTED); c.setFont('Helvetica-Bold',8); c.drawCentredString(x+116,95,'CUT OUT')
 footer(c,num,w)

def page_pack_cover(c,w,num,accent):
 book=w['books3']; theme=w.get('theme','Read, notice, and tell what happens.')
 c.setFillColor(PAPER); c.rect(0,0,W,H,fill=1,stroke=0)
 c.setFillColor(accent); c.roundRect(0,H-162,W,162,0,fill=1,stroke=0)
 c.setFillColor(white); c.setFont('Helvetica-Bold',11); c.drawString(44,H-48,f"WEEK {w['n']}  •  STORY ACTIVITY BOOK")
 para(c,book,44,H-69,430,'display',66)
 c.setFillColor(white); c.setFont('Helvetica',15); c.drawString(46,H-142,'Look · talk · play · make')
 icon(c,BOOKS[w['n']]['icon'],W-135,H-138,165)
 rounded(c,42,430,528,92,HexColor('#FFF8E7'),GOLD,15,sw=1.5)
 c.setFillColor(INK); c.setFont('Helvetica-Bold',14); c.drawString(61,489,'THIS WEEK’S STORY IDEA')
 para(c,theme,61,470,487,'body',54)
 items=[('STORY TALK',PUR,LAV),('WORD PLAY',TEAL,MINT),('COUNT & COLOR',GOLD,PALE),('DRAW & RETELL',CORAL,PINK)]
 for i,(label,col,fill) in enumerate(items):
  x=43+(i%2)*270; y=337-(i//2)*82
  rounded(c,x,y,255,63,fill,col,13,sw=1.2)
  c.setFillColor(col); c.circle(x+29,y+31,16,fill=1,stroke=0); c.setFillColor(white); c.setFont('Helvetica-Bold',11); c.drawCentredString(x+29,y+27,str(i+1))
  c.setFillColor(INK); c.setFont('Helvetica-Bold',13); c.drawString(x+57,y+26,label)
 c.setFillColor(INK); c.setFont('Helvetica-Bold',14); c.drawString(45,145,'THIS ACTIVITY BOOK BELONGS TO')
 line_set(c,45,92,500,spacing=30)
 c.setFillColor(MUTED); c.setFont('Helvetica',10); c.drawRightString(545,55,'Point, tell, draw, match, or write your answer.')
 footer(c,num,w)

def page_word_detective(c,w,num,accent):
 header(c,w,LESSONS_BY_WEEK[w['n']][0],'Book-word detectives',accent)
 para(c,'Look at each picture. Say or point to the word. Find its first letter, then trace or copy it.',40,635,W-80,'body',38)
 cards=BOOKS[w['n']]['cards'][:4]
 for i,(word,k) in enumerate(cards):
  y=424-i*91; acc=[PUR,TEAL,GOLD,CORAL][i]
  rounded(c,40,y,532,78,[LAV,MINT,PALE,PINK][i],acc,13,sw=1.25)
  icon(c,k,83,y+40,57,tile_idx=i)
  c.setFillColor(INK); c.setFont('Helvetica-Bold',17); c.drawString(127,y+48,word.title())
  c.setFillColor(MUTED); c.setFont('Helvetica-Bold',10); c.drawString(127,y+28,'FIRST LETTER')
  c.setFillColor(white); c.setStrokeColor(LINE); c.roundRect(219,y+15,34,38,8,fill=1,stroke=1)
  c.setFillColor(acc); c.setFont('Helvetica-Bold',22); c.drawCentredString(236,y+23,word[0])
  c.setFillColor(MUTED); c.setFont('Helvetica-Bold',10); c.drawString(275,y+49,'TRACE OR WRITE THE WORD')
  line_set(c,275,y+17,280,spacing=24)
 rounded(c,40,66,532,63,white,HexColor('#D7CBE5'),12,sw=1)
 c.setFillColor(PUR); c.setFont('Helvetica-Bold',12); c.drawString(56,106,'MY FAVORITE BOOK WORD')
 line_set(c,220,77,330,spacing=24)
 footer(c,num,w)

def page_rhyme_match(c,w,num,accent):
 header(c,w,LESSONS_BY_WEEK[w['n']][0],'Rhyme-and-match center',accent)
 para(c,'Say the picture word. Circle the choice that rhymes. Point, say, or mark your answer.',40,635,W-80,'body',38)
 prompts=RHYMES[w['n']]
 for i,(target,rhyme,decoy) in enumerate(prompts):
  y=385-i*125; acc=[PUR,TEAL,GOLD][i]; fill=[LAV,MINT,PALE][i]
  rounded(c,40,y,532,108,white,acc,14,sw=1.3)
  art_idx=RHYME_ART[w['n']][i]; art_kind=BOOKS[w['n']]['cards'][art_idx][1]
  icon(c,art_kind,92,y+56,66,tile_idx=art_idx)
  c.setFillColor(INK); c.setFont('Helvetica-Bold',18); c.drawString(141,y+70,target.title())
  c.setFillColor(MUTED); c.setFont('Helvetica-Bold',10); c.drawString(141,y+49,'WHICH WORD RHYMES?')
  choices=[rhyme,decoy] if i%2==0 else [decoy,rhyme]
  for j,choice in enumerate(choices):
   x=303+j*122; rounded(c,x,y+27,109,47,fill if j==0 else HexColor('#F4F7FB'),acc,11,sw=1)
   c.setFillColor(INK); c.setFont('Helvetica-Bold',16); c.drawCentredString(x+54.5,y+43,choice.title())
  c.setFillColor(MUTED); c.setFont('Helvetica',9); c.drawString(142,y+12,'Say both words. Do they sound the same at the end?')
 rounded(c,40,70,532,57,HexColor('#FFF8E7'),GOLD,12,sw=1)
 c.setFillColor(INK); c.setFont('Helvetica-Bold',12); c.drawString(56,105,'MAKE A RHYME')
 para(c,'Draw or write one more word that rhymes with a book word.',160,111,395,'small',35)
 footer(c,num,w)

def page_counting_center(c,w,num,accent):
 header(c,w,LESSONS_BY_WEEK[w['n']][0],'Count the story pictures',accent)
 para(c,'Touch each picture as you count. Write the number, match a number card, or tell your answer.',40,635,W-80,'body',38)
 kind=BOOKS[w['n']]['icon']
 for i,count in enumerate([1,2,3,4,5]):
  y=482-i*82; acc=[PUR,TEAL,GOLD,CORAL,BLUE][i]
  rounded(c,40,y,532,70,[LAV,MINT,PALE,PINK,HexColor('#E9F1F9')][i],acc,12,sw=1.1)
  c.setFillColor(acc); c.circle(72,y+35,17,fill=1,stroke=0); c.setFillColor(white); c.setFont('Helvetica-Bold',14); c.drawCentredString(72,y+30,str(count))
  gap=64; start=122
  for j in range(count): icon(c,kind,start+j*gap,y+35,44,tile_idx=(j+i)%min(9,len(BOOKS[w['n']]['cards'])))
  c.setFillColor(MUTED); c.setFont('Helvetica-Bold',10); c.drawString(444,y+44,'HOW MANY?')
  c.setStrokeColor(LINE); c.setFillColor(white); c.roundRect(458,y+8,92,28,8,fill=1,stroke=1)
  c.setFillColor(acc); c.setFont('Helvetica-Bold',16); c.drawCentredString(504,y+16,'_____')
 footer(c,num,w)

def page_color_code(c,w,num,accent):
 header(c,w,LESSONS_BY_WEEK[w['n']][0],'Solve • color • reveal',accent)
 para(c,'Solve each little addition problem. Use the color key to fill the matching squares and reveal a book-themed picture.',40,635,W-80,'body',42)
 labels=[('4','2 + 2',PUR,LAV),('5','2 + 3',GOLD,PALE),('6','3 + 3',TEAL,MINT)]
 x=48
 for answer,equation,col,fill in labels:
  rounded(c,x,536,166,50,fill,col,12,sw=1.2); c.setFillColor(col); c.setFont('Helvetica-Bold',16); c.drawString(x+12,554,answer+' = '+equation); c.setFillColor(MUTED); c.setFont('Helvetica-Bold',9); c.drawRightString(x+154,555,'COLOR')
  x+=178
 mask=MASKS[w['n']]; cellw=74; cellh=47; x0=(W-cellw*6)/2; ytop=510
 for row,line in enumerate(mask):
  for col,filled in enumerate(line):
   if filled!='#': continue
   x=x0+col*cellw; y=ytop-(row+1)*cellh
   rounded(c,x,y,cellw-3,cellh-3,white,[PUR,GOLD,TEAL][(row+col+w['n'])%3],5,sw=.8)
   equation=['2+2','2+3','3+3'][(row*2+col+w['n'])%3]
   c.setFillColor(INK); c.setFont('Helvetica-Bold',11); c.drawCentredString(x+(cellw-3)/2,y+17,equation)
 c.setFillColor(MUTED); c.setFont('Helvetica-Bold',10); c.drawCentredString(W/2,177,'COLOR THE SHAPE. THEN DRAW A DETAIL FROM YOUR BOOK.')
 icon(c,BOOKS[w['n']]['icon'],W/2,115,68)
 footer(c,num,w)

def draw_model(c,kind,cx,cy,size,step):
 """Draw an original, easy-to-copy four-step picture cue using vector shapes."""
 s=size/100; c.saveState(); c.translate(cx-size/2,cy-size/2); c.scale(s,s)
 c.setStrokeColor(INK); c.setFillColor(HexColor('#FFFDF8')); c.setLineWidth(3.2)
 def line(x1,y1,x2,y2): c.line(x1,y1,x2,y2)
 def oval(x,y,ww,hh,fill=0): c.ellipse(x,y,x+ww,y+hh,fill=fill,stroke=1)
 if kind=='broom':
  if step>=1: line(16,30,85,72)
  if step>=2:
   c.setLineWidth(2.4)
   for dx in [12,20,28,36,44]: line(17+dx*.22,29-dx*.25,5+dx*.22,8-dx*.12)
  if step>=3: oval(16,28,16,9)
  if step>=4: draw_star(c,75,82,5); draw_star(c,86,87,3)
 elif kind=='pumpkin':
  if step>=1: oval(21,22,58,48)
  if step>=2:
   for xx in [33,45,57]: c.arc(xx,24,xx+17,69,90,180)
  if step>=3: c.roundRect(47,69,10,12,3,fill=0,stroke=1); line(53,76,66,82)
  if step>=4: line(46,51,50,51); line(61,51,65,51); c.arc(47,40,64,52,200,140)
 elif kind=='bowl':
  if step>=1: c.arc(20,48,80,82,180,180)
  if step>=2: line(20,63,28,30); line(80,63,72,30); c.arc(28,14,72,48,180,180); line(23,62,77,62)
  if step>=3: oval(34,49,10,8); oval(50,51,10,8); oval(63,48,8,8)
  if step>=4:
   for x in [39,55,68]: c.arc(x,72,x+10,88,90,180)
 elif kind in ('leaf','tree','appletree'):
  if kind=='leaf':
   if step>=1: line(17,20,81,80)
   if step>=2:
    c.bezier(17,20,22,65,55,82,81,80); c.bezier(17,20,51,20,72,48,81,80)
   if step>=3:
    for a,b,d,e in [(30,34,28,51),(42,45,37,65),(55,57,47,73),(67,67,58,78)]: line(a,b,d,e)
   if step>=4: line(17,20,8,13); draw_star(c,83,84,4)
  else:
   if step>=1: line(45,18,45,56); line(57,18,57,56)
   if step>=2: line(51,52,22,82); line(51,52,78,82); line(51,42,29,61); line(51,42,73,61)
   if step>=3:
    for x,y in [(28,73),(42,80),(60,80),(74,72),(38,61),(62,61)]: oval(x,y,16,14)
   if step>=4 and kind=='appletree':
    for x,y in [(32,72),(51,78),(68,67)]: c.circle(x,y,3,fill=0,stroke=1)
 elif kind=='penguin':
  if step>=1: oval(28,16,44,70)
  if step>=2: oval(36,23,29,42)
  if step>=3: c.circle(40,66,3,fill=1,stroke=1); c.circle(60,66,3,fill=1,stroke=1); line(46,57,54,57); line(54,57,50,51); line(50,51,46,57)
  if step>=4: line(38,16,31,10); line(61,16,69,10); line(27,49,17,43); line(73,49,83,43); draw_star(c,50,88,5)
 elif kind=='snowman':
  if step>=1: c.circle(50,20,12,fill=0,stroke=1)
  if step>=2: c.circle(50,44,17,fill=0,stroke=1); c.circle(50,75,12,fill=0,stroke=1)
  if step>=3: c.setFillColor(GOLD); c.setStrokeColor(GOLD); p=c.beginPath(); p.moveTo(62,75); p.lineTo(78,71); p.lineTo(62,68); p.close(); c.drawPath(p,fill=1,stroke=0); c.setStrokeColor(INK); c.setFillColor(HexColor('#FFFDF8')); c.circle(45,78,1.6,fill=1,stroke=1); c.circle(55,78,1.6,fill=1,stroke=1)
  if step>=4: line(32,49,18,59); line(68,49,82,59); draw_star(c,20,84,5); draw_star(c,82,82,4)
 elif kind=='footprints':
  if step>=1: oval(36,20,11,21); oval(57,56,11,21)
  if step>=2:
   oval(56,18,11,21); oval(34,58,11,21)
  if step>=3:
   c.setLineWidth(2); c.arc(8,8,92,43,0,180); line(17,25,83,25)
  if step>=4:
   draw_star(c,18,80,5); draw_star(c,82,82,5); draw_star(c,50,90,4)
 c.restoreState()

def page_directed_draw(c,w,num,accent):
 title,kind=DRAWING[w['n']]
 header(c,w,LESSONS_BY_WEEK[w['n']][0],'Draw it step by step',accent)
 para(c,f'Look at the book picture. Follow the four drawing steps, then make your own big {title.lower()}.',40,635,W-80,'body',40)
 labels=['START WITH A SHAPE','ADD THE MAIN PARTS','ADD BOOK DETAILS','FINISH & COLOR']
 for i,label in enumerate(labels):
  col=i%2; row=i//2; x=40+col*272; y=330-row*211
  rounded(c,x,y,260,194,[LAV,MINT,PALE,PINK][i],[PUR,TEAL,GOLD,CORAL][i],14,sw=1.25)
  c.setFillColor([PUR,TEAL,GOLD,CORAL][i]); c.setFont('Helvetica-Bold',10); c.drawString(x+13,y+173,f'STEP {i+1}')
  c.setFillColor(INK); c.setFont('Helvetica-Bold',11); c.drawRightString(x+246,y+173,label)
  draw_model(c,kind,x+130,y+97,112,i+1)
  if i==3:
   c.setStrokeColor(LINE); c.setDash(4,3); c.roundRect(x+15,y+12,230,32,8,fill=0,stroke=1); c.setDash()
   c.setFillColor(MUTED); c.setFont('Helvetica',10); c.drawCentredString(x+130,y+23,'MY OWN DETAIL: __________________')
 rounded(c,40,80,532,34,HexColor('#FFF7E6'),GOLD,9,sw=1)
 c.setFillColor(INK); c.setFont('Helvetica-Bold',11); c.drawCentredString(W/2,92,'NOW DRAW YOUR OWN BIG PICTURE ON THE BACK OR A BLANK PAGE')
 footer(c,num,w)

def page_retell_wheel(c,w,num,accent):
 header(c,w,LESSONS_BY_WEEK[w['n']][0],'Cut • spin • retell',accent)
 para(c,'Cut out the wheel. Point to each step as you tell, sign, or show what happened in the book.',40,635,W-80,'body',38)
 cx,cy=220,343; r=190
 colors=[PUR,TEAL,GOLD,CORAL]; fills=[LAV,MINT,PALE,PINK]; labels=['FIRST','NEXT','THEN','LAST']
 for i in range(4):
  start=90-i*90; c.setFillColor(fills[i]); c.setStrokeColor(colors[i]); c.setLineWidth(2)
  c.wedge(cx-r,cy-r,cx+r,cy+r,start,-90,fill=1,stroke=1)
  a=math.radians(start-45); tx=cx+112*math.cos(a); ty=cy+112*math.sin(a)
  c.setFillColor(colors[i]); c.setFont('Helvetica-Bold',15); c.drawCentredString(tx,ty+8,labels[i])
  kind=BOOKS[w['n']]['events'][i][1]; icon(c,kind,tx,ty-28,54,tile_idx=min(i,8))
 c.setFillColor(PAPER); c.setStrokeColor(INK); c.circle(cx,cy,30,fill=1,stroke=1)
 c.setFillColor(INK); c.setFont('Helvetica-Bold',8); c.drawCentredString(cx,cy-2,'BOOK')
 c.setStrokeColor(PUR); c.setLineWidth(2); c.setDash(5,4); c.circle(cx,cy,r+8,fill=0,stroke=1); c.setDash()
 rounded(c,440,145,132,355,HexColor('#FBF7FF'),HexColor('#D8C8E8'),14,sw=1)
 c.setFillColor(PUR); c.setFont('Helvetica-Bold',12); c.drawCentredString(506,470,'SPINNER')
 for i,label in enumerate(labels):
  y=420-i*58; c.setFillColor(colors[i]); c.circle(465,y,13,fill=1,stroke=0); c.setFillColor(white); c.setFont('Helvetica-Bold',11); c.drawCentredString(465,y-4,str(i+1)); c.setFillColor(INK); c.setFont('Helvetica-Bold',11); c.drawString(490,y-4,label.title())
 c.setFillColor(PUR); p=c.beginPath(); p.moveTo(470,218); p.lineTo(533,218); p.lineTo(533,212); p.lineTo(552,224); p.lineTo(533,236); p.lineTo(533,230); p.lineTo(470,230); p.close(); c.drawPath(p,fill=1,stroke=0)
 c.setFillColor(PAPER); c.setStrokeColor(INK); c.circle(477,224,3,fill=1,stroke=1)
 c.setFillColor(MUTED); c.setFont('Helvetica-Bold',8); c.drawCentredString(506,201,'CUT OUT THE ARROW')
 c.setFillColor(PUR); c.setFont('Helvetica-Bold',7); c.drawCentredString(506,188,'ADD FASTENER AT CENTER')
 c.setFillColor(MUTED); c.setFont('Helvetica',8); c.drawCentredString(506,177,'Or point to each step.')
 c.setFillColor(INK); c.setFont('Helvetica-Bold',10); c.drawString(40,102,'MY STORY CLUE:')
 writing_rows(c,143,67,410,2,spacing=20,gap=5)
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
 core_path=ROOT/'work'/f'week-{n}-student-printables-core.pdf'; core_path.parent.mkdir(parents=True,exist_ok=True)
 pdf=canvas.Canvas(str(core_path),pagesize=letter)
 pdf.setTitle(f'Week {n} student printables • {book}'); pdf.setAuthor('Stacie Classroom')
 # Start directly with the student work; the weekly art and layout stay consistent.
 page_num=1
 page_pack_cover(pdf,w,page_num,ACCENTS[n-1]); pdf.showPage(); page_num+=1
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
   cards=bookdata['cards']; cw=250; gapx=22; gapy=10; x0=45; ytop=H-128
   row_count=math.ceil(len(cards)/2); ch=min(180,(ytop-82-(row_count-1)*gapy)/row_count)
   for i,(label,k) in enumerate(cards):
    col=i%2; row=i//2; x=x0+col*(cw+gapx); y=ytop-(row+1)*ch-row*gapy
    rounded(pdf,x,y,cw,ch,[LAV,MINT,PALE,PINK,HexColor('#E8F1F9')][i%5],[PUR,TEAL,GOLD,CORAL,BLUE][i%5],12,dash=True,sw=1.25)
    if ch>=150:
     icon(pdf,k,x+cw/2,y+ch*.61,min(105,ch*.56),tile_idx=min(i,8))
     pdf.setFillColor(INK); pdf.setFont('Helvetica-Bold',17); pdf.drawCentredString(x+cw/2,y+24,label[:24])
    else:
     size=min(82,ch*.62); icon(pdf,k,x+58,y+ch/2,size,tile_idx=min(i,8))
     pdf.setFillColor(INK); pdf.setFont('Helvetica-Bold',15); pdf.drawString(x+108,y+ch/2-5,label[:19])
   pdf.showPage(); page_num+=1
 # Craft/activity page is student-facing; no teacher procedure block.
 page_craft(pdf,w,page_num,ACCENTS[n-1]); pdf.showPage(); pdf.save()
 # Keep the resource choices available both as individual mini-packets and as
 # one convenient activity-center bundle. The combined student pack contains all.
 resources={
  'literacy-centers': [page_word_detective,page_rhyme_match],
  'math-centers': [page_counting_center,page_color_code],
  'directed-drawing': [page_directed_draw],
  'retell-wheel': [page_retell_wheel],
 }
 part_paths=[]
 for resource,builders in resources.items():
  part=OUT/f'week-{n}-{resource}.pdf'; part_paths.append(part)
  p=canvas.Canvas(str(part),pagesize=letter); p.setTitle(f'Week {n} {resource.replace("-"," ")} • {book}'); p.setAuthor('Stacie Classroom')
  for i,builder in enumerate(builders,1): builder(p,w,i,ACCENTS[n-1]); p.showPage()
  p.save()
 from pypdf import PdfReader, PdfWriter
 centers=OUT/f'week-{n}-activity-centers.pdf'; cw=PdfWriter()
 for part in part_paths: cw.append(str(part),outline_item=part.stem.replace('-', ' '))
 cw.write(str(centers)); cw.close()
 final=PdfWriter(); final.append(str(core_path),outline_item='Daily book activities')
 final.append(str(centers),outline_item='Optional activity centers')
 total=len(final.pages); final.write(str(path)); final.close(); core_path.unlink()
 print(path.name,book,f'{total} pages, plus 4 activity downloads')
