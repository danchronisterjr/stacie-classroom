"""Build one original, student-facing reading/craft pack for each shared weekly book."""
import json, math, pathlib, re, datetime, random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import HexColor, white
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from PIL import Image

ROOT=pathlib.Path(__file__).resolve().parents[1]
DATA=(ROOT/'dist/data.js').read_text()
WEEKS=json.JSONDecoder().raw_decode(DATA.split('const WEEKS=',1)[1])[0]
LESSONS=json.JSONDecoder().raw_decode(DATA.split('const LESSONS=',1)[1])[0]
OUT=ROOT/'dist/resources'
ART_RAW=ROOT/'scripts/art/raw'
ART_CROPS=ROOT/'scripts/art/crops'
PDF_ART=ROOT/'work/printable-art'
W,H=letter

# A friendly classroom-printable display face gives the activity sheets the
# playful, teacher-made feel of the reference packets while keeping body copy
# in a highly readable sans serif.
KID_FONT='/System/Library/Fonts/Supplemental/Comic Sans MS.ttf'
KID_BOLD_FONT='/System/Library/Fonts/Supplemental/Comic Sans MS Bold.ttf'
if pathlib.Path(KID_FONT).exists() and pathlib.Path(KID_BOLD_FONT).exists():
 pdfmetrics.registerFont(TTFont('KidPrint',KID_FONT))
 pdfmetrics.registerFont(TTFont('KidPrint-Bold',KID_BOLD_FONT))
 pdfmetrics.registerFontFamily('KidPrint',normal='KidPrint',bold='KidPrint-Bold',italic='KidPrint',boldItalic='KidPrint-Bold')
else:
 # The fallback keeps the generator portable to non-macOS build hosts.
 pdfmetrics.registerFontAlias('KidPrint','Helvetica')
 pdfmetrics.registerFontAlias('KidPrint-Bold','Helvetica-Bold')

PUR=HexColor('#7145A3'); LAV=HexColor('#F1E9F8'); TEAL=HexColor('#188579'); MINT=HexColor('#E7F5F1')
GOLD=HexColor('#E5A52F'); PALE=HexColor('#FFF3D9'); CORAL=HexColor('#E87759'); PINK=HexColor('#FCE9E4')
BLUE=HexColor('#397EB8'); INK=HexColor('#293654'); MUTED=HexColor('#5D6B83'); LINE=HexColor('#D6DFE9'); PAPER=HexColor('#FFFEFB')
STYLES={
 'body':ParagraphStyle('body',fontName='KidPrint',fontSize=15,leading=19,textColor=INK),
 'small':ParagraphStyle('small',fontName='KidPrint',fontSize=13,leading=16.5,textColor=MUTED),
 'center':ParagraphStyle('center',fontName='KidPrint-Bold',fontSize=13.5,leading=17,alignment=TA_CENTER,textColor=INK),
 'white':ParagraphStyle('white',fontName='KidPrint-Bold',fontSize=13,leading=16,textColor=white),
 'display':ParagraphStyle('display',fontName='KidPrint-Bold',fontSize=24,leading=29,textColor=white),
}

BOOKS={
 1:{'icon':'witch','cards':[('WITCH','witch'),('CAT','cat'),('DOG','dog'),('BIRD','bird'),('FROG','frog'),('DRAGON','dragon'),('BROOM','broom'),('HAT','hat'),('BOW','bow'),('WAND','wand')],
    'events':[('The wind blows the witch’s hat away.','hat'),('A dog finds it and joins the ride.','dog'),('The broom breaks, and the friends fall into a bog.','broom'),('The friends scare the dragon; the witch makes a new broom.','witch')],
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

# Short, paraphrased story sentences for accessible picture-supported practice.
# These are not quotations from the books.
CLOZE={
 1:[('The wind blows the witch’s ____ away.','HAT','hat'),('A ____ finds the lost hat.','DOG','dog'),('A ____ comes near the friends.','DRAGON','dragon'),('The witch makes a ____ broom.','NEW','broom')],
 2:[('The witch grows a very ____ pumpkin.','BIG','pumpkin'),('The friends try to ____ it.','PULL','helper'),('The ____ has a plan.','BAT','bat'),('At the end, friends share pumpkin ____.','PIE','pumpkin')],
 3:[('The friends make ____ soup.','PUMPKIN','pumpkin'),('Each friend has a special ____.','JOB','helper'),('Duck wants a turn to ____.','STIR','wand'),('The friends make soup ____.','TOGETHER','bowl')],
 4:[('The wind carries the ____.','LEAVES','leaf'),('The leaves make pictures of ____.','ANIMALS','bird'),('Leaf Man travels through many ____.','PLACES','place'),('The wind keeps the leaves ____.','MOVING','wind')],
 5:[('The friends go on a leaf ____.','HUNT','leaf'),('They travel through the ____.','WOODS','tree'),('They look for colorful ____.','LEAVES','leaf'),('At the end, the friends go ____.','HOME','home')],
 6:[('Fletcher sees leaves fall from the ____.','TREE','tree'),('He tries to help his ____.','TREE','tree'),('The last ____ floats away.','LEAF','leaf'),('Fletcher discovers something ____.','SPECIAL','star')],
 7:[('In spring, the tree begins to ____.','GROW','flower'),('In summer, the tree is full of ____.','LEAVES','leaf'),('In fall, the tree has ____.','APPLES','tree'),('In winter, the tree ____.','RESTS','snow')],
 8:[('The ____ family gets ready for winter.','PENGUIN','penguin'),('They put on warm ____.','CLOTHES','coat'),('The family goes into the ____.','SNOW','snow'),('They find a way to enjoy the ____.','DAY','sun')],
 9:[('Peter wakes up to see ____.','SNOW','snow'),('Peter leaves ____ in the snow.','FOOTPRINTS','footprints'),('He plays with a ____.','SNOWBALL','snowball'),('The next ____ brings more snow.','DAY','sun')],
}

CRAFTS={
 1:('Make room for one more helper','Color the story pictures. Cut each friend out and glue them into a broom seat. Draw a new helper of your own.',('COLOR THE FRIENDS','CUT THEM OUT','GLUE & TELL')),
 2:('Help the giant pumpkin','Cut out the helpers. Place them around the pumpkin to show how they work together.',('MEET THE TEAM','HELP PULL','SHARE THE PUMPKIN')),
 3:('Make a soup story bowl','Cut out the story friends and soup pictures. Place the ingredients in the bowl, then tell who helped.',('CHOOSE THE SOUP','ADD THE FRIENDS','TELL WHO HELPED')),
 4:('Build a Leaf Man','Cut out leaf pictures to build a Leaf Man. Add a place where the wind could carry him.',('MAKE A LEAF SHAPE','ADD A PLACE','SHOW THE WIND')),
 5:('Map a leaf hunt','Cut out the leaves and places. Put them along the trail in the order the friends visit.',('START THE HUNT','FIND A LEAF','GO TO THE NEXT PLACE')),
 6:('Help Fletcher’s tree','Cut out the leaf pictures. Show the tree before, during, and after the leaves fall.',('TREE BEFORE','LEAVES FALL','TREE AFTER')),
 7:('Make a four-season tree','Cut out the season pictures. Place each season around the same tree.',('SPRING','SUMMER & FALL','WINTER')),
 8:('Dress for a snowy day','Cut out the winter clothes. Give the penguin a warm outfit for a snowy day.',('GET READY','DRESS WARMLY','PLAY IN THE SNOW')),
 9:('Make a snowy-day path','Cut out the snow-day pictures. Place them along Peter’s walk in story order.',('START THE WALK','LEAVE FOOTPRINTS','WHAT HAPPENS NEXT?')),
}

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
 PDF_ART.mkdir(parents=True,exist_ok=True)
 for src in list(ART_CROPS.glob('week-*-tile-*.png'))+[ART_CROPS/'week-1-bow.png']:
  # A 256-colour transparent palette keeps the original 480px print detail
  # while substantially reducing the embedded art in each PDF.
  dst=PDF_ART/src.name
  with Image.open(src) as opened:
   opened.convert('RGBA').quantize(colors=256,method=Image.Quantize.FASTOCTREE,dither=Image.Dither.FLOYDSTEINBERG).save(dst,optimize=True)

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
 path=PDF_ART/'week-1-bow.png' if CURRENT_WEEK==1 and kind=='bow' else PDF_ART/f'week-{CURRENT_WEEK}-tile-{tile_idx}.png'
 c.drawImage(ImageReader(str(path)),cx-size/2,cy-size/2,size,size,mask='auto',preserveAspectRatio=True,anchor='c')

def header(c,w,lesson,title,accent):
 c.setFillColor(PAPER); c.rect(0,0,W,H,fill=1,stroke=0)
 c.setFillColor(accent); c.roundRect(38,H-66,5,29,2,fill=1,stroke=0)
 date=datetime.date.fromisoformat(lesson['date']).strftime('%A, %B %d').replace(' 0',' ') if lesson else 'STUDENT ACTIVITY'
 c.setFillColor(accent); c.setFont('Helvetica-Bold',10); c.drawString(52,H-48,f"WEEK {w['n']}  •  {date}")
 c.setFillColor(INK); title_size=23
 while title_size>18 and stringWidth(title,'KidPrint-Bold',title_size)>W-145: title_size-=.5
 c.setFont('KidPrint-Bold',title_size); c.drawString(39,H-91,title)
 c.setFillColor(MUTED); c.setFont('Helvetica-Bold',9); c.drawString(40,H-116,w['books3'].upper())
 icon(c,BOOKS[w['n']]['icon'],W-83,H-77,82)
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
 header(c,w,None,'Cut • place • retell',accent)
 para(c,'Choose the four cut-apart story cards. Place them in order, then tell what happened.',40,635,W-80,'body',32)
 labels=[('FIRST',LAV,PUR,'first'),('NEXT',MINT,TEAL,'next'),('THEN',PALE,GOLD,'helper'),('LAST',PINK,CORAL,'last')]
 for i,(lab,fill,acc,kind) in enumerate(labels):
  col=i%2; row=i//2; x=40+col*272; y=358-row*224
  rounded(c,x,y,260,208,white,acc,14,sw=1.5)
  pill(c,lab,x+14,y+174,fill,acc,100)
  icon(c,kind,x+220,y+180,42)
  c.setStrokeColor(LINE); c.setDash(5,4); c.roundRect(x+12,y+12,236,148,12,fill=0,stroke=1); c.setDash()
  c.setFillColor(MUTED); c.setFont('Helvetica-Bold',9); c.drawCentredString(x+130,y+81,'PLACE A STORY CARD HERE')
 footer(c,num,w)

def page_event_cards(c,w,num,accent):
 header(c,w,None,'Cut-apart story event cards',accent)
 para(c,'Cut on the dotted lines. Put the pictures in order, match them to the book, or use them to retell.',40,635,W-80,'body',35)
 events=BOOKS[w['n']]['events']; fills=[LAV,MINT,PALE,PINK]; accents=[PUR,TEAL,GOLD,CORAL]
 for i,(text,kind) in enumerate(events):
  col=i%2; row=i//2; x=40+col*272; y=358-row*224
  rounded(c,x,y,260,208,fills[i],accents[i],14,dash=True,sw=1.8)
  pill(c,f'PICTURE {i+1}',x+13,y+177,white,accents[i],100)
  icon(c,kind,x+78,y+105,98)
  para(c,text,x+137,y+156,105,'center',95)
  c.setFillColor(MUTED); c.setFont('Helvetica-Bold',8.5); c.drawCentredString(x+130,y+15,'CUT APART ON THE DOTTED LINE')
 footer(c,num,w)

def page_story_map(c,w,num,accent):
 header(c,w,None,'Story map • who, where, what, how',accent)
 para(c,'Use the book pictures. Point, draw, add a card, or write one idea in each part.',40,635,W-80,'body',34)
 sections=[('WHO IS HERE?','Name or show a character.','witch',LAV,PUR),('WHERE ARE THEY?','Find the place in the story.','place',MINT,TEAL),('WHAT CHANGES?','Show the problem or big event.','problem',PALE,GOLD),('HOW DOES IT END?','Show what happens after.','last',PINK,CORAL)]
 for i,(label,prompt,kind,fill,acc) in enumerate(sections):
  col=i%2; row=i//2; x=40+col*272; y=356-row*224
  rounded(c,x,y,260,208,white,acc,14,sw=1.5)
  c.setFillColor(fill); c.roundRect(x+12,y+171,236,24,8,fill=1,stroke=0)
  c.setFillColor(acc); c.setFont('Helvetica-Bold',12); c.drawString(x+21,y+179,label)
  icon(c,kind,x+218,y+149,56)
  c.setFillColor(MUTED); c.setFont('Helvetica',9.5); c.drawString(x+16,y+145,prompt)
  c.setStrokeColor(LINE); c.setDash(4,3); c.roundRect(x+14,y+52,232,80,9,fill=0,stroke=1); c.setDash()
  c.setFillColor(MUTED); c.setFont('Helvetica-Bold',8); c.drawString(x+22,y+119,'DRAW OR PLACE A PICTURE')
  writing_rows(c,x+19,y+11,220,1,spacing=21,gap=5)
 footer(c,num,w)

def page_picture_match(c,w,num,accent):
 header(c,w,None,'Picture • word match',accent)
 para(c,'Look at the story pictures. Match each picture to its word by drawing a line, pointing, or placing a word card.',40,635,W-80,'body',40)
 cards=BOOKS[w['n']]['cards'][:4]
 # Put the picture cards in story order and scramble the matching word column.
 order=[2,0,3,1] if w['n']%2 else [1,3,0,2]
 for i,(word,kind) in enumerate(cards):
  y=437-i*93; acc=[PUR,TEAL,GOLD,CORAL][i]; fill=[LAV,MINT,PALE,PINK][i]
  rounded(c,40,y,192,78,fill,acc,12,sw=1.3)
  icon(c,kind,83,y+39,61,tile_idx=i)
  c.setFillColor(INK); c.setFont('Helvetica-Bold',13); c.drawString(123,y+35,f'PICTURE {i+1}')
  c.setStrokeColor(acc); c.setLineWidth(1.7); c.circle(211,y+39,10,fill=0,stroke=1)
  dest=order[i]; dw=cards[dest][0]
  rounded(c,380,y,192,78,white,acc,12,sw=1.3)
  c.setFillColor(INK); c.setFont('Helvetica-Bold',17); c.drawCentredString(476,y+32,dw.title())
  c.setFillColor(MUTED); c.setFont('Helvetica-Bold',8); c.drawCentredString(476,y+15,'WORD CARD')
  c.setStrokeColor(LINE); c.setLineWidth(.8); c.line(237,y+39,375,y+39)
 rounded(c,40,61,532,55,HexColor('#FFF8E7'),GOLD,12,sw=1.2)
 c.setFillColor(INK); c.setFont('Helvetica-Bold',12); c.drawString(56,94,'MY STORY WORD')
 c.setFillColor(MUTED); c.setFont('Helvetica',10); c.drawString(178,94,'Choose one word. Copy it or draw what it means.')
 line_set(c,56,71,496,spacing=20)
 footer(c,num,w)

def make_maze(seed,rows=8,cols=8):
 rng=random.Random(seed); walls={(r,c):{'N','E','S','W'} for r in range(rows) for c in range(cols)}
 seen={(0,0)}; stack=[(0,0)]; dirs=[('N',-1,0,'S'),('E',0,1,'W'),('S',1,0,'N'),('W',0,-1,'E')]
 while stack:
  r,c=stack[-1]; choices=[(d,r+dr,c+dc,back) for d,dr,dc,back in dirs if 0<=r+dr<rows and 0<=c+dc<cols and (r+dr,c+dc) not in seen]
  if not choices: stack.pop(); continue
  d,nr,nc,back=rng.choice(choices); walls[(r,c)].remove(d); walls[(nr,nc)].remove(back); seen.add((nr,nc)); stack.append((nr,nc))
 return walls

def page_story_maze(c,w,num,accent):
 header(c,w,None,'Follow the story path',accent)
 word=BOOKS[w['n']]['cards'][0][0].title(); goal=BOOKS[w['n']]['cards'][1][0].title()
 para(c,f'Help {word} find {goal}. Trace the open path from START to FINISH.',40,635,W-80,'body',32)
 rows=8; cols=8; cell=51; x0=(W-cols*cell)/2; y0=100; walls=make_maze(w['n']*17+5,rows,cols)
 c.saveState(); c.setStrokeColor(INK); c.setLineWidth(2.1)
 for r in range(rows):
  for col in range(cols):
   x=x0+col*cell; y=y0+(rows-1-r)*cell; cell_walls=walls[(r,col)]
   if 'N' in cell_walls:c.line(x,y+cell,x+cell,y+cell)
   if 'W' in cell_walls:c.line(x,y,x,y+cell)
   if r==rows-1 and 'S' in cell_walls:c.line(x,y,x+cell,y)
   if col==cols-1 and 'E' in cell_walls:c.line(x+cell,y,x+cell,y+cell)
 c.restoreState()
 icon(c,BOOKS[w['n']]['cards'][0][1],x0+cell/2,y0+(rows-.5)*cell,38,tile_idx=0)
 icon(c,BOOKS[w['n']]['cards'][1][1],x0+(cols-.5)*cell,y0+cell/2,38,tile_idx=1)
 c.setFillColor(PUR); c.setFont('Helvetica-Bold',9); c.drawCentredString(x0+cell/2,y0+rows*cell+7,'START')
 c.setFillColor(TEAL); c.drawCentredString(x0+(cols-.5)*cell,y0-15,'FINISH')
 footer(c,num,w)

def page_favorite_scene(c,w,num,accent):
 header(c,w,None,'Draw • tell • write',accent)
 para(c,'Find a part you remember from the book. Draw the scene, then tell or write about it.',40,635,W-80,'body',35)
 rounded(c,40,247,532,330,white,accent,16,sw=1.7)
 c.setFillColor([LAV,MINT,PALE,PINK][(w['n']-1)%4]); c.roundRect(55,536,502,26,9,fill=1,stroke=0)
 c.setFillColor(accent); c.setFont('Helvetica-Bold',12); c.drawString(70,544,'MY FAVORITE BOOK SCENE')
 icon(c,BOOKS[w['n']]['icon'],521,503,66)
 c.setStrokeColor(LINE); c.setLineWidth(1.2); c.setDash(5,4); c.roundRect(58,283,496,233,11,fill=0,stroke=1); c.setDash()
 c.setFillColor(MUTED); c.setFont('Helvetica-Bold',9); c.drawCentredString(W/2,492,'DRAW A BIG PICTURE. ADD THE CHARACTERS AND DETAILS.')
 c.setFillColor(INK); c.setFont('Helvetica-Bold',13); c.drawString(48,211,'My favorite part is…')
 writing_rows(c,49,81,515,4,spacing=24,gap=7)
 footer(c,num,w)

def page_character_sticks(c,w,num,accent):
 header(c,w,None,'Character story sticks',accent)
 para(c,'Color, cut out, and add a paper strip behind each picture. Use the characters to retell the story.',40,635,W-80,'body',35)
 cards=BOOKS[w['n']]['cards'][:4]
 for i,(label,kind) in enumerate(cards):
  col=i%2; row=i//2; x=40+col*272; y=355-row*226; acc=[PUR,TEAL,GOLD,CORAL][i]; fill=[LAV,MINT,PALE,PINK][i]
  rounded(c,x,y,260,210,fill,acc,14,dash=True,sw=1.7)
  icon(c,kind,x+130,y+126,104,tile_idx=i)
  c.setFillColor(INK); c.setFont('Helvetica-Bold',15); c.drawCentredString(x+130,y+45,label.title())
  c.setStrokeColor(acc); c.setLineWidth(1.5); c.line(x+111,y+22,x+149,y+22)
  c.setFillColor(MUTED); c.setFont('Helvetica-Bold',8); c.drawCentredString(x+130,y+10,'TAPE A PAPER STRIP HERE')
 footer(c,num,w)

def page_story_words(c,w,num,accent):
 header(c,w,None,'My story words',accent)
 para(c,'Choose a word from the picture cards. Trace it, say its first sound, then use it to tell about the book.',40,635,W-80,'body',36)
 for i,(word,kind) in enumerate(BOOKS[w['n']]['cards'][:4]):
  y=433-i*97; acc=[PUR,TEAL,GOLD,CORAL][i]; fill=[LAV,MINT,PALE,PINK][i]
  rounded(c,40,y,532,84,white,acc,13,sw=1.35)
  c.setFillColor(fill); c.roundRect(50,y+9,100,66,10,fill=1,stroke=0); icon(c,kind,100,y+42,58,tile_idx=i)
  c.setFillColor(INK); c.setFont('Helvetica-Bold',16); c.drawString(166,y+52,word.title())
  c.setFillColor(MUTED); c.setFont('Helvetica-Bold',9); c.drawString(166,y+31,'FIRST SOUND')
  c.setStrokeColor(LINE); c.setFillColor(white); c.roundRect(250,y+22,35,37,7,fill=1,stroke=1)
  c.setFillColor(acc); c.setFont('Helvetica-Bold',20); c.drawCentredString(267.5,y+31,word[0])
  c.setFillColor(MUTED); c.setFont('Helvetica-Bold',9); c.drawString(302,y+51,'TRACE / COPY')
  c.setFillColor(HexColor('#AAB4C3')); c.setFont('Helvetica-Bold',18); c.drawString(302,y+24,word.title())
 rounded(c,40,53,532,46,HexColor('#FFF8E7'),GOLD,10,sw=1)
 c.setFillColor(INK); c.setFont('Helvetica-Bold',11); c.drawString(56,78,'I can use this word to tell…')
 line_set(c,234,60,319,spacing=20)
 footer(c,num,w)

def page_story_cloze(c,w,num,accent):
 header(c,w,None,'Finish the story ideas',accent)
 para(c,'Choose a word from the picture bank. Point, say, place a card, or write to finish each sentence.',40,635,W-80,'body',36)
 rows=CLOZE[w['n']]
 for i,(_,answer,kind) in enumerate(rows):
  x=42+i*132; rounded(c,x,487,124,72,[LAV,MINT,PALE,PINK][i],[PUR,TEAL,GOLD,CORAL][i],11,sw=1.2)
  icon(c,kind,x+34,523,44)
  c.setFillColor(INK); c.setFont('Helvetica-Bold',9.5); c.drawString(x+59,519,answer)
 c.setFillColor(MUTED); c.setFont('Helvetica-Bold',9); c.drawString(43,464,'PICTURE WORD BANK')
 for i,(sentence,_answer,kind) in enumerate(rows):
  y=359-i*91; acc=[PUR,TEAL,GOLD,CORAL][i]
  rounded(c,40,y,532,79,white,acc,13,sw=1.25)
  c.setFillColor(acc); c.circle(70,y+40,17,fill=1,stroke=0); c.setFillColor(white); c.setFont('Helvetica-Bold',12); c.drawCentredString(70,y+36,str(i+1))
  icon(c,kind,119,y+40,48)
  para(c,sentence,158,y+56,392,'body',55)
 footer(c,num,w)

def page_picture_pattern(c,w,num,accent):
 header(c,w,None,'Finish the picture pattern',accent)
 para(c,'Look at the story pictures. What comes next? Choose a picture from the two choices.',40,635,W-80,'body',34)
 cards=BOOKS[w['n']]['cards']; patterns=[[0,1,0,1,None],[0,0,1,0,0,None],[0,1,2,0,1,None],[1,2,1,2,None]]
 for r,pattern in enumerate(patterns):
  y=440-r*96; acc=[PUR,TEAL,GOLD,CORAL][r]; fill=[LAV,MINT,PALE,PINK][r]
  rounded(c,40,y,532,79,white,acc,12,sw=1.15)
  for j,idx in enumerate(pattern):
   x=50+j*48
   rounded(c,x,y+13,43,52,fill if idx is not None else white,acc,8,dash=(idx is None),sw=1)
   if idx is None:
    c.setFillColor(acc); c.setFont('Helvetica-Bold',22); c.drawCentredString(x+21.5,y+28,'?')
   else:
    icon(c,cards[idx%len(cards)][1],x+21.5,y+39,38,tile_idx=idx)
  answers=[0,1,2,1]; choices=(answers[r],(answers[r]+1)%len(cards))
  for j,idx in enumerate(choices):
   x=369+j*94; rounded(c,x,y+8,86,64,fill,acc,9,sw=1)
   c.setFillColor(acc); c.circle(x+14,y+58,8,fill=1,stroke=0); c.setFillColor(white); c.setFont('Helvetica-Bold',7.5); c.drawCentredString(x+14,y+55,'AB'[j])
   icon(c,cards[idx%len(cards)][1],x+49,y+39,47,tile_idx=idx)
 rounded(c,40,64,532,44,HexColor('#FFF8E7'),GOLD,10,sw=1)
 c.setFillColor(INK); c.setFont('Helvetica-Bold',10.5); c.drawCentredString(W/2,79,'SAY IT • POINT TO IT • CIRCLE A OR B')
 footer(c,num,w)

def page_character_detective(c,w,num,accent):
 header(c,w,None,'Character detective',accent)
 para(c,'Look at what a character does in the story. Use a picture clue, an action, or a feeling to tell about them.',40,635,W-80,'body',38)
 prompts=[('LOOKS LIKE','Find a picture clue.','first'),('SAYS OR DOES','Show one action.','helper'),('FEELS','How might the character feel?','question'),('CHANGES OR HELPS','What happens because of them?','result')]
 for i,(label,question,kind) in enumerate(prompts):
  y=430-i*96; acc=[PUR,TEAL,GOLD,CORAL][i]; fill=[LAV,MINT,PALE,PINK][i]
  rounded(c,40,y,532,82,white,acc,13,sw=1.25)
  c.setFillColor(fill); c.roundRect(51,y+10,82,62,9,fill=1,stroke=0); icon(c,kind,92,y+41,55)
  c.setFillColor(acc); c.setFont('Helvetica-Bold',11); c.drawString(145,y+55,label)
  c.setFillColor(MUTED); c.setFont('Helvetica',9.5); c.drawString(145,y+36,question)
  line_set(c,145,y+9,404,spacing=18)
 rounded(c,40,49,532,42,HexColor('#FFF8E7'),GOLD,10,sw=1)
 c.setFillColor(INK); c.setFont('Helvetica-Bold',10.5); c.drawCentredString(W/2,64,'I CAN SHOW MY ANSWER WITH A PICTURE, WORD, SIGN, OR AAC.')
 footer(c,num,w)

def page_picture_puzzle(c,w,num,accent):
 header(c,w,None,'Cut • mix • rebuild the picture',accent)
 para(c,'Color the story picture. Cut on the lines, mix the pieces, and put the picture back together.',40,635,W-80,'body',34)
 side=410; x0=(W-side)/2; y0=120
 rounded(c,x0-7,y0-7,side+14,side+14,white,accent,10,sw=1.8)
 icon(c,BOOKS[w['n']]['icon'],W/2,y0+side/2,side-12)
 c.saveState(); c.setStrokeColor(INK); c.setLineWidth(1.7); c.setDash(5,3)
 for i in (1,2):
  xx=x0+i*side/3; yy=y0+i*side/3
  c.line(xx,y0,xx,y0+side); c.line(x0,yy,x0+side,yy)
 c.restoreState()
 c.setFillColor(MUTED); c.setFont('Helvetica-Bold',9); c.drawCentredString(W/2,96,'CUT ON THE DOTTED LINES • PUT THE STORY PICTURE BACK TOGETHER')
 footer(c,num,w)

def page_cover_creator(c,w,num,accent):
 header(c,w,None,'Make a new book cover',accent)
 para(c,'Draw a favorite story moment on the cover. Add a title picture, then tell what the reader will see.',40,635,W-80,'body',35)
 x,y,bw,bh=90,122,432,438
 rounded(c,x,y,bw,bh,white,accent,18,sw=2)
 c.setFillColor([LAV,MINT,PALE,PINK][(w['n']-1)%4]); c.roundRect(x+14,y+bh-57,bw-28,39,10,fill=1,stroke=0)
 c.setFillColor(accent); c.setFont('Helvetica-Bold',13); c.drawCentredString(W/2,y+bh-43,w['books3'].upper())
 icon(c,BOOKS[w['n']]['icon'],W-113,y+bh-43,46)
 c.setStrokeColor(LINE); c.setDash(5,4); c.roundRect(x+22,y+97,bw-44,bh-184,12,fill=0,stroke=1); c.setDash()
 c.setFillColor(MUTED); c.setFont('Helvetica-Bold',9); c.drawCentredString(W/2,y+bh-81,'DRAW A SCENE THAT MAKES SOMEONE WANT TO READ')
 c.setFillColor(INK); c.setFont('Helvetica-Bold',11); c.drawString(x+25,y+66,'MY COVER SHOWS…')
 writing_rows(c,x+25,y+18,bw-50,1,spacing=22,gap=5)
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
 title,prompt,steps=CRAFTS[w['n']]
 header(c,w,None,title,accent)
 para(c,prompt,40,635,W-80,'body',42)
 rounded(c,40,218,532,354,HexColor('#FFF9EC'),GOLD,17,sw=1.6)
 c.setFillColor(PALE); c.roundRect(52,531,508,28,10,fill=1,stroke=0)
 c.setFillColor(INK); c.setFont('KidPrint-Bold',12); c.drawCentredString(W/2,539,'STORY-MAKING MAT')
 for i,label in enumerate(steps):
  x=52+i*170; acc=[PUR,TEAL,GOLD][i]; fill=[LAV,MINT,PALE][i]
  rounded(c,x,494,162,25,fill,acc,10,sw=1)
  c.setFillColor(acc); c.setFont('KidPrint-Bold',8.2); c.drawCentredString(x+81,502,label)
 # Make the student page a usable cut-and-place activity instead of a blank
 # craft-planning form. The shared story art is the anchor for every book.
 if w['n']==1:
  draw_model(c,'broom',300,366,216,4)
  seats=[(293,355),(324,375),(355,395)]
  for i,(sx,sy) in enumerate(seats,1):
   c.setFillColor(white); c.setStrokeColor(PUR); c.setLineWidth(1.7); c.setDash(4,3); c.circle(sx,sy,19,fill=1,stroke=1); c.setDash()
   c.setFillColor(PUR); c.setFont('KidPrint-Bold',10); c.drawCentredString(sx,sy-4,str(i))
  # The directions already explain the seats; keep the broom art unobstructed.
 elif w['n']==5:
  # This is a route-map craft, so give students an actual trail with three
  # picture stops rather than a large leaf-shaped placeholder.
  path=c.beginPath(); path.moveTo(107,332); path.curveTo(160,397,246,414,306,419); path.curveTo(377,423,431,390,505,332)
  c.saveState(); c.setStrokeColor(TEAL); c.setLineWidth(5); c.setDash(8,6); c.drawPath(path,fill=0,stroke=1); c.restoreState()
  stops=[(107,332,'START'),(306,419,'FIND A LEAF'),(505,332,'HEAD HOME')]
  for i,(sx,sy,label) in enumerate(stops,1):
   acc=[PUR,TEAL,GOLD][i-1]; fill=[LAV,MINT,PALE][i-1]
   c.setFillColor(white); c.setStrokeColor(acc); c.setLineWidth(2); c.setDash(4,3); c.circle(sx,sy,33,fill=1,stroke=1); c.setDash()
   c.setFillColor(acc); c.setFont('KidPrint-Bold',10); c.drawCentredString(sx,sy-4,str(i))
   c.setFillColor(INK); c.setFont('KidPrint-Bold',9); c.drawCentredString(sx,sy-49,label)
 else:
  # Each week gets a big scene image plus clear places to add the story pieces.
  hero={6:'tree'}.get(w['n'],BOOKS[w['n']]['icon'])
  icon(c,hero,306,373,184)
  slots={2:[(170,340),(442,340),(306,276)],3:[(195,338),(306,338),(417,338)],
         4:[(175,338),(306,338),(437,338)],5:[(160,335),(306,335),(452,335)],
         6:[(188,350),(306,390),(424,350)],7:[(176,342),(436,342),(176,273),(436,273)],
         8:[(180,340),(432,340),(306,270)],9:[(170,330),(306,330),(442,330)]}[w['n']]
  for i,(sx,sy) in enumerate(slots,1):
   c.setFillColor(HexColor('#FFFEFC')); c.setStrokeColor([PUR,TEAL,GOLD,CORAL][(i-1)%4]); c.setLineWidth(1.5); c.setDash(4,3); c.circle(sx,sy,22,fill=1,stroke=1); c.setDash()
   c.setFillColor([PUR,TEAL,GOLD,CORAL][(i-1)%4]); c.setFont('KidPrint-Bold',10); c.drawCentredString(sx,sy-4,str(i))
  c.setFillColor(MUTED); c.setFont('Helvetica-Bold',9); c.drawCentredString(306,250,'GLUE A STORY PICTURE IN EACH NUMBERED SPOT')
 # Four large matching cut-outs make this page ready to use.
 cards=BOOKS[w['n']]['cards'][:4]
 for i,(label,kind) in enumerate(cards):
  x=40+i*136; acc=[PUR,TEAL,GOLD,CORAL][i]; fill=[LAV,MINT,PALE,PINK][i]
  rounded(c,x,67,126,112,fill,acc,12,dash=True,sw=1.5)
  icon(c,kind,x+63,130,61,tile_idx=i)
  c.setFillColor(INK); c.setFont('KidPrint-Bold',10); c.drawCentredString(x+63,91,label[:18])
  c.setFillColor(MUTED); c.setFont('Helvetica-Bold',8); c.drawCentredString(x+63,77,'CUT THIS PICTURE')
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
 header(c,w,None,'Book-word detectives',accent)
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
 header(c,w,None,'Rhyme-and-match center',accent)
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
 header(c,w,None,'Count the story pictures',accent)
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
 header(c,w,None,'Solve • color • reveal',accent)
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
  wood=HexColor('#8B5429'); shine=HexColor('#C58B4A'); bristle=HexColor('#E5B34E'); edge=HexColor('#A7662A')
  if step>=1:
   c.setStrokeColor(wood); c.setLineWidth(8); line(35,44,91,80)
   c.setStrokeColor(shine); c.setLineWidth(1.6); line(38,45,89,78)
  if step>=2:
   c.setFillColor(bristle); c.setStrokeColor(edge); c.setLineWidth(1.8)
   # Broad, unmistakable fan of broom straw attached to the lower end of
   # the handle; the profile stays clean when printed small or copied.
   p=c.beginPath(); p.moveTo(33,42); p.lineTo(41,47); p.lineTo(27,17); p.lineTo(22,7); p.lineTo(17,2); p.lineTo(12,7); p.lineTo(7,4); p.lineTo(4,12); p.lineTo(0,14); p.lineTo(2,23); p.lineTo(5,31); p.lineTo(13,36); p.lineTo(23,40); p.close(); c.drawPath(p,fill=1,stroke=1)
  if step>=3:
   c.setStrokeColor(HexColor('#B8752B')); c.setLineWidth(1.15)
   for x1,y1,x2,y2 in [(2,17,35,44),(5,11,36,44),(11,6,36,44),(17,4,37,45),(4,26,34,43),(10,33,35,43),(17,38,37,45),(23,40,39,46)]: line(x1,y1,x2,y2)
   c.setStrokeColor(HexColor('#6F421F')); c.setLineWidth(3.2); line(32,40,39,49)
  if step>=4:
   c.setStrokeColor(HexColor('#D39B35')); c.setLineWidth(2); line(34,41,40,47); line(36,39,42,45)
   c.setFillColor(GOLD); draw_star(c,76,83,5); draw_star(c,86,69,3.5)
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
 header(c,w,None,'Draw it step by step',accent)
 para(c,f'Look at the book picture. Follow the four drawing steps, then make your own big {title.lower()}.',40,635,W-80,'body',40)
 labels=(['DRAW THE HANDLE','ADD A BRISTLE FAN','TIE & TEXTURE','ADD A STAR & COLOR'] if kind=='broom' else ['START WITH A SHAPE','ADD THE MAIN PARTS','ADD BOOK DETAILS','FINISH & COLOR'])
 for i,label in enumerate(labels):
  col=i%2; row=i//2; x=40+col*272; y=330-row*211
  rounded(c,x,y,260,194,[LAV,MINT,PALE,PINK][i],[PUR,TEAL,GOLD,CORAL][i],14,sw=1.25)
  c.setFillColor([PUR,TEAL,GOLD,CORAL][i]); c.setFont('Helvetica-Bold',10); c.drawString(x+13,y+173,f'STEP {i+1}')
  c.setFillColor(INK); c.setFont('Helvetica-Bold',11); c.drawRightString(x+246,y+173,label)
  draw_model(c,kind,x+130,y+105,140,i+1)
  if i==3:
   c.setStrokeColor(LINE); c.setDash(4,3); c.roundRect(x+15,y+8,230,26,8,fill=0,stroke=1); c.setDash()
   c.setFillColor(MUTED); c.setFont('Helvetica',9); c.drawCentredString(x+130,y+16,'MY OWN DETAIL: __________________')
 rounded(c,40,80,532,34,HexColor('#FFF7E6'),GOLD,9,sw=1)
 c.setFillColor(INK); c.setFont('KidPrint-Bold',11); c.drawCentredString(W/2,92,'NEXT: MAKE YOUR OWN BIG PICTURE ON THE DRAW & WRITE PAGE')
 footer(c,num,w)

def page_retell_wheel(c,w,num,accent):
 header(c,w,None,'Cut • spin • retell',accent)
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
 # A short, student-facing activity sampler follows the daily pages. Each
 # sheet is a complete hands-on choice with original book art and work space.
 add_on_pages=[
  (page_event_cards,'Cut-apart story events'),
  (page_story_map,'Story map'),
  (page_picture_match,'Picture and word match'),
  (page_story_cloze,'Finish the story ideas'),
  (page_picture_pattern,'Picture pattern'),
  (page_character_detective,'Character detective'),
  (page_story_maze,'Story path puzzle'),
  (page_picture_puzzle,'Cut-apart picture puzzle'),
  (page_favorite_scene,'Draw and write'),
  (page_character_sticks,'Character story sticks'),
  (page_cover_creator,'Design a new cover'),
 ]
 if not any(day_kind(l,di,len(lessons),n)=='sequence' for di,l in enumerate(lessons)):
  add_on_pages.insert(1,(page_sequence,'Story sequence mat'))
 for builder,_label in add_on_pages:
  builder(pdf,w,page_num,ACCENTS[n-1]); pdf.showPage(); page_num+=1
 # The make-it page is student-facing and uses this book's own story cues.
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
