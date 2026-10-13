"""Build one original, student-facing reading/craft pack for each shared weekly book."""
import json, math, pathlib, re, datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import HexColor, white
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.pdfbase.pdfmetrics import stringWidth

ROOT=pathlib.Path(__file__).resolve().parents[1]
DATA=(ROOT/'dist/data.js').read_text()
WEEKS=json.JSONDecoder().raw_decode(DATA.split('const WEEKS=',1)[1])[0]
LESSONS=json.JSONDecoder().raw_decode(DATA.split('const LESSONS=',1)[1])[0]
OUT=ROOT/'dist/resources'
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
def icon(c,kind,cx,cy,size):
 # Friendly, original vector symbols: generic story clues, not book illustrations.
 scale=size/100; c.saveState(); c.translate(cx-size/2,cy-size/2); c.scale(scale,scale)
 bg={'witch':LAV,'cat':HexColor('#EEF1F5'),'dog':PALE,'fox':HexColor('#FFF0DE'),'bird':HexColor('#FFF1C9'),'frog':MINT,'dragon':PINK,'broom':PALE,'hat':LAV,'bow':PINK,'wand':HexColor('#E8F1F9'),'book':HexColor('#E8F1F9'),'place':MINT,'question':PALE,'first':LAV,'next':MINT,'last':PINK,'problem':PINK,'helper':MINT,'result':PALE,'star':HexColor('#FFF1C9'),'pumpkin':HexColor('#FFF0DE'),'bowl':PINK,'leaf':MINT,'wind':HexColor('#E8F1F9'),'tree':MINT,'home':PALE,'flower':PINK,'sun':PALE,'apple':PINK,'snow':HexColor('#E8F1F9'),'penguin':HexColor('#E8F1F9'),'child':LAV,'coat':PINK,'boots':HexColor('#FFF0DE'),'footprints':HexColor('#E8F1F9'),'ghost':white,'vampire':LAV,'mummy':HexColor('#F5F1E9'),'bat':HexColor('#E8F1F9')}
 c.setFillColor(bg.get(kind,PALE)); c.setStrokeColor(HexColor('#D8E1EB')); c.setLineWidth(2); c.circle(50,50,47,fill=1,stroke=1)
 def face(color):
  c.setFillColor(color); c.circle(50,50,31,fill=1,stroke=0); c.setFillColor(INK); c.circle(40,55,3,fill=1,stroke=0); c.circle(60,55,3,fill=1,stroke=0); c.setStrokeColor(INK); c.setLineWidth(2); c.arc(39,34,62,51,200,140)
 if kind in ('witch','child','vampire'):
  if kind=='vampire':
   c.setFillColor(PUR); path=c.beginPath(); path.moveTo(20,55); path.lineTo(32,12); path.lineTo(50,29); path.lineTo(68,12); path.lineTo(80,55); path.close(); c.drawPath(path,fill=1,stroke=0)
  face(HexColor('#F0B690'))
  if kind=='witch':
   c.setFillColor(PUR); path=c.beginPath(); path.moveTo(15,70); path.lineTo(50,98); path.lineTo(82,70); path.close(); c.drawPath(path,fill=1,stroke=0); c.setFillColor(GOLD); c.ellipse(19,66,81,73,fill=1,stroke=0)
  elif kind=='child':
   c.setFillColor(HexColor('#6D4A39')); c.wedge(19,57,81,91,0,180,fill=1,stroke=0)
  else:
   c.setFillColor(white); path=c.beginPath(); path.moveTo(42,37); path.lineTo(47,47); path.lineTo(50,37); path.lineTo(54,47); path.lineTo(59,37); path.close(); c.drawPath(path,fill=1,stroke=0)
 elif kind in ('cat','dog','fox','frog','ghost'):
  color={'cat':HexColor('#717F91'),'dog':HexColor('#C87943'),'fox':CORAL,'frog':TEAL,'ghost':white}[kind]
  c.setFillColor(color)
  if kind in ('cat','fox'):
   path=c.beginPath(); path.moveTo(20,63); path.lineTo(18,91); path.lineTo(40,78); path.lineTo(60,78); path.lineTo(82,91); path.lineTo(80,63); path.close(); c.drawPath(path,fill=1,stroke=0)
  elif kind=='dog':c.ellipse(15,50,32,83,fill=1,stroke=0); c.ellipse(68,50,85,83,fill=1,stroke=0)
  face(color)
 elif kind in ('bird','bat','penguin'):
  if kind=='bat':
   c.setFillColor(PUR); t=c.beginPath(); t.moveTo(50,69); t.curveTo(37,88,27,74,15,81); t.lineTo(21,54); t.lineTo(12,61); t.curveTo(13,35,31,33,50,48); t.curveTo(69,33,87,35,88,61); t.lineTo(79,54); t.lineTo(85,81); t.curveTo(73,74,63,88,50,69); t.close(); c.drawPath(t,fill=1,stroke=0); c.setFillColor(GOLD); c.circle(42,59,2,fill=1,stroke=0); c.circle(58,59,2,fill=1,stroke=0)
  elif kind=='bird':
   c.setFillColor(GOLD); c.ellipse(18,32,80,77,fill=1,stroke=0); c.ellipse(52,62,92,92,fill=1,stroke=0); c.setFillColor(CORAL); t=c.beginPath(); t.moveTo(86,67); t.lineTo(99,61); t.lineTo(87,55); t.close(); c.drawPath(t,fill=1,stroke=0)
   c.setFillColor(INK); c.circle(72,73,3,fill=1,stroke=0)
  else:
   c.setFillColor(INK); c.ellipse(20,17,80,88,fill=1,stroke=0); c.setFillColor(white); c.ellipse(32,24,68,70,fill=1,stroke=0); c.setFillColor(GOLD); t=c.beginPath(); t.moveTo(45,63); t.lineTo(55,63); t.lineTo(50,54); t.close(); c.drawPath(t,fill=1,stroke=0); c.ellipse(34,10,46,17,fill=1,stroke=0); c.ellipse(55,10,67,17,fill=1,stroke=0)
 elif kind=='mummy':
  c.setFillColor(HexColor('#E9E3D8')); c.roundRect(21,21,58,58,23,fill=1,stroke=0); c.setStrokeColor(HexColor('#BEB5A7')); c.setLineWidth(4)
  for yy in [33,43,53,63,73]:c.line(25,yy,75,yy)
  c.setFillColor(INK); c.circle(41,58,3,fill=1,stroke=0); c.circle(59,58,3,fill=1,stroke=0)
 elif kind=='dragon':
  c.setFillColor(CORAL); c.circle(49,50,31,fill=1,stroke=0); t=c.beginPath(); t.moveTo(25,72); t.lineTo(28,94); t.lineTo(45,74); t.close(); c.drawPath(t,fill=1,stroke=0); t=c.beginPath(); t.moveTo(57,74); t.lineTo(78,94); t.lineTo(75,68); t.close(); c.drawPath(t,fill=1,stroke=0); c.setFillColor(INK); c.circle(40,55,3,fill=1,stroke=0); c.circle(60,55,3,fill=1,stroke=0); c.setStrokeColor(INK); c.arc(39,34,62,51,200,140)
 elif kind in ('broom','hat','bow','wand'):
  if kind=='broom':c.setStrokeColor(HexColor('#8B5A34')); c.setLineWidth(8); c.line(25,34,78,79); c.setFillColor(GOLD); t=c.beginPath(); t.moveTo(18,24); t.lineTo(40,45); t.lineTo(25,66); t.lineTo(12,55); t.close(); c.drawPath(t,fill=1,stroke=0)
  elif kind=='hat':c.setFillColor(PUR); t=c.beginPath(); t.moveTo(20,42); t.lineTo(48,85); t.lineTo(68,42); t.close(); c.drawPath(t,fill=1,stroke=0); c.setFillColor(GOLD); c.ellipse(13,35,84,49,fill=1,stroke=0)
  elif kind=='bow':c.setFillColor(CORAL); t=c.beginPath(); t.moveTo(46,50); t.lineTo(16,77); t.lineTo(19,36); t.close(); c.drawPath(t,fill=1,stroke=0); t=c.beginPath(); t.moveTo(54,50); t.lineTo(84,77); t.lineTo(81,36); t.close(); c.drawPath(t,fill=1,stroke=0); c.circle(50,52,8,fill=1,stroke=0)
  else:c.setStrokeColor(PUR); c.setLineWidth(7); c.line(28,29,73,73); c.setFillColor(GOLD); draw_star(c,75,77,14)
 elif kind=='pumpkin':
  c.setFillColor(CORAL); c.ellipse(18,26,82,75,fill=1,stroke=0); c.setFillColor(HexColor('#F49A48')); c.ellipse(34,23,66,78,fill=1,stroke=0); c.setFillColor(TEAL); c.roundRect(45,73,10,13,3,fill=1,stroke=0); c.setFillColor(INK); c.circle(41,51,3,fill=1,stroke=0); c.circle(59,51,3,fill=1,stroke=0); c.setStrokeColor(INK); c.arc(40,36,60,49,200,140)
 elif kind=='bowl':
  c.setFillColor(CORAL); c.ellipse(21,48,79,68,fill=1,stroke=0); c.setFillColor(HexColor('#F5B44A')); c.wedge(22,24,78,60,180,180,fill=1,stroke=0); c.setStrokeColor(PUR); c.setLineWidth(3); c.arc(27,19,73,50,180,180)
 elif kind=='leaf':
  c.setFillColor(GOLD); c.ellipse(22,26,78,78,fill=1,stroke=0); c.setStrokeColor(TEAL); c.setLineWidth(3); c.line(27,30,75,75); c.line(43,45,39,67); c.line(55,56,69,52)
 elif kind=='wind':
  c.setStrokeColor(BLUE); c.setLineWidth(5)
  for y in [37,51,65]:c.arc(17,y,83,y+20,0,180)
  c.setFillColor(GOLD); draw_star(c,74,73,10)
 elif kind in ('tree','apple'):
  c.setFillColor(HexColor('#8B5A34')); c.roundRect(43,18,14,48,4,fill=1,stroke=0); c.setFillColor(TEAL); c.circle(50,67,25,fill=1,stroke=0); c.circle(34,57,17,fill=1,stroke=0); c.circle(67,57,17,fill=1,stroke=0)
  if kind=='apple':c.setFillColor(CORAL); c.circle(38,61,6,fill=1,stroke=0); c.circle(66,70,6,fill=1,stroke=0); c.circle(55,48,6,fill=1,stroke=0)
 elif kind in ('snow','sun','flower','star'):
  if kind=='snow':
   c.setStrokeColor(BLUE); c.setLineWidth(4)
   for a in [0,60,120]:
    c.saveState(); c.translate(50,50); c.rotate(a); c.line(-28,0,28,0); c.line(20,0,13,7); c.line(20,0,13,-7); c.restoreState()
  elif kind=='sun':c.setFillColor(GOLD); c.circle(50,50,20,fill=1,stroke=0); c.setStrokeColor(GOLD); c.setLineWidth(5)
  elif kind=='flower':
   c.setFillColor(CORAL)
   for a in range(0,360,60):c.saveState(); c.translate(50,50); c.rotate(a); c.ellipse(-9,20,9,38,fill=1,stroke=0); c.restoreState()
   c.setFillColor(GOLD); c.circle(50,50,9,fill=1,stroke=0)
  else:c.setFillColor(GOLD); draw_star(c,50,50,28)
 elif kind in ('place','home'):
  c.setFillColor(TEAL if kind=='place' else GOLD); t=c.beginPath(); t.moveTo(18,50); t.lineTo(50,80); t.lineTo(82,50); t.lineTo(73,50); t.lineTo(73,25); t.lineTo(57,25); t.lineTo(57,43); t.lineTo(50,50); t.close(); c.drawPath(t,fill=1,stroke=0)
 elif kind=='coat':
  c.setFillColor(CORAL); t=c.beginPath(); t.moveTo(34,78); t.lineTo(18,65); t.lineTo(27,38); t.lineTo(34,43); t.lineTo(37,22); t.lineTo(63,22); t.lineTo(66,43); t.lineTo(73,38); t.lineTo(82,65); t.lineTo(66,78); t.close(); c.drawPath(t,fill=1,stroke=0)
 elif kind=='boots':
  c.setFillColor(PUR); c.roundRect(24,28,21,49,5,fill=1,stroke=0); c.roundRect(55,28,21,49,5,fill=1,stroke=0); c.setFillColor(GOLD); c.rect(20,22,28,9,fill=1,stroke=0); c.rect(52,22,28,9,fill=1,stroke=0)
 elif kind=='footprints':
  c.setFillColor(BLUE); c.ellipse(23,22,48,49,fill=1,stroke=0); c.ellipse(53,54,78,81,fill=1,stroke=0)
 elif kind=='question':
  c.setFillColor(PUR); c.setFont('Helvetica-Bold',57); c.drawCentredString(50,31,'?')
 elif kind in ('first','next','last'):
  c.setFillColor(PUR if kind=='first' else TEAL if kind=='next' else CORAL); c.setFont('Helvetica-Bold',54); c.drawCentredString(50,31,'1' if kind=='first' else '→' if kind=='next' else '★')
 elif kind in ('problem','helper','result'):
  if kind=='problem':c.setFillColor(CORAL); c.roundRect(23,30,54,43,8,fill=1,stroke=0); c.setFillColor(white); c.setFont('Helvetica-Bold',24); c.drawCentredString(50,39,'!')
  elif kind=='helper':c.setFillColor(TEAL); c.circle(50,53,19,fill=1,stroke=0); c.setFillColor(GOLD); draw_star(c,50,53,10)
  else:c.setFillColor(GOLD); draw_star(c,50,53,28)
 c.restoreState()

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
 icon(c,BOOKS[w['n']]['icon'],W/2,352,100)
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
for w in WEEKS:
 n=w['n']; lessons=LESSONS_BY_WEEK[n]; book=w['books3']; assert book==w['books4'],f'Week {n}: shared books diverge'
 bookdata=BOOKS[n]; path=OUT/f'week-{n}-student-printables.pdf'
 # Week 1 is the teacher-approved illustrated PDF in dist/resources. Keep that exact artifact.
 if n==1:
  if not path.exists(): raise FileNotFoundError(f'Place the approved Week 1 student PDF at {path}')
  print(path.name,book,'approved source PDF preserved')
  continue
 pdf=canvas.Canvas(str(path),pagesize=letter)
 pdf.setTitle(f'Week {n} student printables • {book}'); pdf.setAuthor('Stacie Classroom')
 # Start directly with student work; the approved Week 1 pack has no separate cover.
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
    rounded(pdf,x,y,cw,ch,[LAV,MINT,PALE,PINK,HexColor('#E8F1F9')][i%5],[PUR,TEAL,GOLD,CORAL,BLUE][i%5],12,dash=True); icon(pdf,k,x+54,y+50,63)
    pdf.setFillColor(INK); pdf.setFont('Helvetica-Bold',13); pdf.drawString(x+105,y+45,label[:19])
   pdf.showPage(); page_num+=1
 # Craft/activity page is student-facing; no teacher procedure block.
 page_craft(pdf,w,page_num,ACCENTS[n-1]); pdf.showPage(); pdf.save()
 print(path.name,book, f'{page_num} pages')
