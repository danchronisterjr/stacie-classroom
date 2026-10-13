import json,pathlib,html
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,PageBreak,Table,TableStyle,KeepTogether
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
ROOT=pathlib.Path(__file__).resolve().parents[1]
P=ROOT/'dist/resources'
raw=(ROOT/'dist/data.js').read_text()
x={k:json.JSONDecoder().raw_decode(raw.split('const '+k+'=',1)[1])[0] for k in ['WEEKS','LESSONS','PLAN_META','TEKS_STANDARDS']}
standards=x['TEKS_STANDARDS']
styles=getSampleStyleSheet();styles.add(ParagraphStyle(name='Text',fontName='Helvetica',fontSize=10.5,leading=15,spaceAfter=7,textColor=colors.HexColor('#17253c')));styles.add(ParagraphStyle(name='Label',fontName='Helvetica-Bold',fontSize=11,leading=15,spaceBefore=10,spaceAfter=5,keepWithNext=True,textColor=colors.HexColor('#2058bc')));styles['Title'].fontSize=23;styles['Title'].leading=28;styles['Title'].textColor=colors.HexColor('#162742');styles['Title'].alignment=TA_LEFT;styles['Heading2'].textColor=colors.HexColor('#2058bc');styles['Heading2'].spaceBefore=12
# Use simple print typography. All special punctuation is normalized for bundled PDF fonts.
def clean(s):return str(s).replace('’',"'").replace('‘',"'").replace('“','"').replace('”','"').replace('–','-').replace('—','-').replace('→',' to ').replace('×',' x ').replace('÷',' / ').replace('−','-').replace('•',' | ').replace('…','...')
def p(s,style='Text'):return Paragraph(html.escape(clean(s)),styles[style])
def section(label,text):return [p(label,'Label'),p(text)]
def footer(c,d):
 c.setStrokeColor(colors.HexColor('#c6d3e5'));c.line(42,38,570,38);c.setFont('Helvetica',8);c.setFillColor(colors.HexColor('#52657b'));c.drawString(42,25,'Stacie | Second nine weeks | Updated October 12, 2026');c.drawRightString(570,25,str(d.page))
def save(name,story):SimpleDocTemplate(str(P/name),pagesize=(612,792),rightMargin=42,leftMargin=42,topMargin=40,bottomMargin=48,title='Stacie teaching calendar',author='Stacie classroom planning').build(story,onFirstPage=footer,onLaterPages=footer)
def title(t,sub=''):return [p(t,'Title')]+([p(sub)] if sub else [])
def table(rows,widths):
 t=Table([[p(v) for v in row] for row in rows],colWidths=widths,repeatRows=1,hAlign='LEFT');t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#edf3ff')),('VALIGN',(0,0),(-1,-1),'TOP'),('BOX',(0,0),(-1,-1),.5,colors.HexColor('#c6d3e5')),('INNERGRID',(0,0),(-1,-1),.4,colors.HexColor('#c6d3e5')),('LEFTPADDING',(0,0),(-1,-1),9),('RIGHTPADDING',(0,0),(-1,-1),9),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8)]));return t
styles['Text'].fontSize=10;styles['Text'].leading=13;styles['Text'].spaceAfter=4
styles['Label'].spaceBefore=6;styles['Label'].spaceAfter=3;styles['Label'].leading=13
for l in x['LESSONS']:
 story=[]
 for j,s in enumerate(l['subjects']):
  if j:story.append(PageBreak())
  story+=title(s['name'],l['date']+' | Week '+str(l['week'])+' | '+l['theme'])
  for g in [3,4]:
   t=s['targets']['g'+str(g)];story+=section('Grade '+str(g)+' | TEKS '+', '.join(t['codes']),' '.join(c+': '+standards[['reading','math','science','social'][j]+':'+c]['official']+' In plain English: '+standards[['reading','math','science','social'][j]+':'+c]['meaning'] for c in t['codes'])+' Today: '+t['skill'])
  story+=section('I Do',s['model'])+section('We Do',s['practice'])+section('You Do',s['check'])
  story+=section('Rotate and switch','Teacher with Grade 3 for 8-10 minutes while Grade 4 uses the taught independent task; switch. Match supports to each learner, not the grade label. Independent task: '+s['independent'])
  story+=section('Access and participation','Use objects or two clear choices, the learner’s planned response method and wait time. Offer a private response or equivalent retry when needed; record extra help and no response separately.')
  story+=section('Evidence and progress',s['evidence'])
  story+=section('Materials',('Real books: '+' / '.join(dict.fromkeys([l['books']['g3']['title'],l['books']['g4']['title']]))+'. Bring the props and response mats in the weekly book guide.') if j==0 else s['materials'])
  if j==0:
   for g in [3,4]:story+=section('Writing TEKS '+str(g)+'.7B',standards['reading:'+str(g)+'.7B']['official'])
   story+=section('Writing and spelling',s['writing'])
   if l.get('seasonal'):story+=section('8-9 AM read-aloud',l['seasonal']['title']+' by '+l['seasonal']['author']+'. Return to the real pages for evidence; see the weekly book guide.')
  if j==2 and l.get('seasonalInvestigation'):story+=section('Friday investigation',l['seasonalInvestigation'])
 save('day-'+l['date']+'.pdf',story)
styles['Text'].fontSize=10.5;styles['Text'].leading=15;styles['Text'].spaceAfter=7
styles['Label'].spaceBefore=10;styles['Label'].spaceAfter=5;styles['Label'].leading=15
for w in x['WEEKS']:
 l=next(l for l in x['LESSONS'] if l['week']==w['n'] and l['friday']);story=title('Week '+str(w['n'])+' | Friday checks',l['date']+' | Three brief items per check. Record accuracy and support separately.')
 story+=section('Spelling','Use three words explicitly taught from each learner’s current HMH sound-spelling pattern. Say the word, use it in a sentence, repeat it. Record encoding separately from supported pattern recognition. Words: __________  __________  __________.')
 for g in [3,4]:
  story+=section('Grade '+str(g)+' reading | '+l['books']['g'+str(g)]['title'],'Use the actual book, with the planned access supports.')
  for i,q in enumerate(l['books']['q'+str(g)]):story+=section(str(i+1)+'. '+q,'Teacher key: '+l['books']['key'+str(g)][i])
 story.append(PageBreak())
 for sub,lab,key in [('math','Math','mathkey'),('sci','Science','scikey')]:
  story+=title(lab+' | Week '+str(w['n']))
  if sub=='sci' and l.get('seasonalInvestigation'):story+=section('Experiment replaces the separate science quiz',l['seasonalInvestigation'])
  for g in [3,4]:
   story+=section('Grade '+str(g),' | '.join(l['subjects'][1 if sub=='math' else 2]['targets']['g'+str(g)]['codes']))
   for i,q in enumerate(l['assessment'][sub+str(g)]):story.append(p(str(i+1)+'. '+q))
   story+=section('Teacher key',l['assessment'][key+str(g)])
  if sub=='math':story.append(PageBreak())
 story+=section('Additional product: '+w['extra'],'Writing: one clear idea, relevant detail/reason and understandable communication. Social studies: a correct person/event or community claim, relevant source evidence and supported connection. Score each criterion 0/1 with prompts noted; apply school grading rules.')
 save('week-'+str(w['n'])+'-friday.pdf',story)
 story=title('Week '+str(w['n'])+' | Real-book guide',w['dates']+' | '+w['theme'])
 for g in [3,4]:
  b=l['books']['g'+str(g)];story+=section('Grade '+str(g)+' | '+b['title'],b['author']+' | '+b['kind']);story+=section('Prepare',b['props']+' '+b['focus'])
  for d in [d for d in x['LESSONS'] if d['week']==w['n']]:
   t=d['subjects'][0]['targets']['g'+str(g)];story.append(p(d['date']+': '+t['skill']+' (TEKS '+', '.join(t['codes'])+')'))
  story+=section('Teach from the actual pages','Read a short section aloud. Think aloud and point to evidence (I Do). Act or sequence it together, then return to the page (We Do). Ask a fresh question and collect the planned response (You Do).')
  if g==3:story.append(PageBreak())
 story+=section('Book access','Borrow a physical book or authorized library/publisher edition. These guides contain teaching prompts, not reproductions of the books. HMH supplies the grade-level reading, writing, drama and spelling selections.')
 save('week-'+str(w['n'])+'-book-guide.pdf',story)
# Family skeleton: plain-language weekly learning, with grades separate.
story=title('Our nine weeks of learning','October 13-December 18, 2026 | Family overview')
story.append(p('We will learn through real books, objects, models and short investigations. Students can show learning by speaking, pointing, arranging pictures, using AAC or writing. We keep a predictable daily routine.'))
for w in x['WEEKS']:
 block=[]
 block+=section('Week '+str(w['n'])+' | '+w['dates'],w['theme']+' | Books: '+w['books3']+(' and '+w['books4'] if w['books3']!=w['books4'] else ''))
 for key,lab in [('reading','Reading and writing'),('math','Math'),('science','Science'),('social','Social studies')]:block.append(p(lab+': Grade 3 - '+w['skills'][key]['g3']['weekly']+' (TEKS '+', '.join(w['skills'][key]['g3']['teks'])+').'+' Grade 4 - '+w['skills'][key]['g4']['weekly']+' (TEKS '+', '.join(w['skills'][key]['g4']['teks'])+').'))
 if w['n']<9:block.append(Spacer(1,10))
 story.append(KeepTogether(block))
story+=section('Friday routine','Each Friday: short spelling, reading, math and science checks. Science experiments: October 23, November 6, November 20 and December 11. The experiment provides the science check evidence. November 23-27 is fall break in this plan.')
story+=section('Individual learning outline','Student: __________  Current learning step: __________  Successful response mode: __________  Helpful supports: __________  Next challenge: __________  Family note: __________. IEP goals will be added after Stacie provides them.')
save('parent-outlines.pdf',story)
story=title('Same routine, every day','Visual sequence: arrive → yoga → library → feelings → preview → read-aloud → subject blocks')
story+=section('8-9 AM | confirmed shared hour','8:00-8:07 yoga. Suggested remaining times: 8:07-8:25 library and return; 8:25-8:32 feelings; 8:32-8:37 learning preview; 8:37-9:00 weekly read-aloud, response and transition. Adjust library timing once to fit the campus schedule, then keep the sequence stable.')
story+=section('Math | 38-minute routine','5 minutes familiar fluency. 3 minutes I Do with the current STEMscopes skill. 5 minutes We Do. Two 10-minute rotations: teacher spends about 6 minutes on the enrolled-grade skill and 4 minutes on placement-selected Bridges work; the other student uses mastered practice or known Vizzle. Finish with 5 minutes of fresh responses and recording. Extend fluency to 10 minutes if the block allows; schedule longer Bridges lessons when needed without compressing program requirements.')
story+=section('All other subjects','Shared start → I Do (3 minutes) → We Do (5 minutes) → first rotation (8-10 minutes) → switch (8-10 minutes) → You Do (3-5 minutes) → record and reset. Set later clock times around the real campus schedule.')
story+=section('Independent work','Previously taught only. Small task tray, clear visual directions, finished basket, planned break signal. Do not assume Grade 4 is more independent. Keep science experiment materials at the supervised station.')
story+=section('Friday','Keep the same visual sequence and teacher rotations. Replace the final practice with three-item checks for spelling, reading, math and science. Every other instructional Friday, use the investigation as the science check.')
story+=section('IEP goals','Awaiting upload. Enter the exact goal, baseline, unit of measurement, response conditions, schedule and reporting dates before calling an activity an IEP probe.')
save('routine.pdf',story)
story=title('Seasonal books and investigations','Stacie’s books are the teaching texts, with hands-on access to the grade-level skills.')
for w in x['WEEKS'][:6]:
 story+=section('Week '+str(w['n'])+' | '+w['seasonal']['title'],w['seasonal']['author']+' | '+w['seasonal']['props']);story.append(p('Grade 3: '+w['seasonal']['g3']+' Grade 4: '+w['seasonal']['g4']+' '+w['seasonal']['evidence']))
story+=section('Informational reading','The Pumpkin Book by Gail Gibbons replaces the former flag book in weeks 1-2. Identify the central idea, find a real growth fact and connect the fact to the idea. Keep this informational strand alongside Room on the Broom.')
for l in x['LESSONS']:
 if l.get('seasonalInvestigation'):story+=section(l['date']+' | Science investigation',l['seasonalInvestigation'])
story+=section('Access and evidence','Props, pictures and AAC support the response. Return to the actual book or investigation evidence. Record accuracy and prompts separately; use three observations on lab Fridays.')
save('seasonal-guide.pdf',story)
story=title('Books to gather','Borrow physical copies or authorized editions; exact page numbers depend on the edition.')
seen=set()
for l in x['LESSONS']:
 for g in ['g3','g4']:
  b=l['books'][g]
  if b['title'] in seen:continue
  seen.add(b['title']);story+=section(b['title'],b['author']+' | '+b['kind']);story.append(p('Prepare: '+b['props']))
save('book-shopping-list.pdf',story)
print('Updated 42 daily PDFs, 9 Friday sets, 9 book guides and 5 planning resources.')# Finish resources left stale by the interrupted build. All filenames remain stable.
keys=['reading','math','science','social'];labels=['Reading and writing','Math','Science','Social studies']
def standard_sections(key,codes):
 out=[]
 for c in codes:out+=section('TEKS '+c,standards[key+':'+c]['official'])+[p('In plain English: '+standards[key+':'+c]['meaning'])]
 return out
story=title('TEKS explained','Grade 3 and Grade 4 | Standards used in this nine-week plan')
story.append(p('Actual student-expectation wording is followed by a plain-English explanation. Capitalization and final punctuation are normalized; 9D(i) includes its introductory clause. These adapted tasks provide access to the standards and do not by themselves establish mastery of every part.'))
for j,key in enumerate(keys):
 if j:story.append(PageBreak())
 story.append(p(labels[j],'Heading1'))
 for g in [3,4]:
  story.append(p('Grade '+str(g),'Heading2'))
  for k,v in standards.items():
   if k.startswith(key+':'+str(g)+'.'):story+=standard_sections(key,[k.split(':')[1]])
story+=section('Authoritative sources, checked October 12, 2026','Texas Education Agency, grade-level TEKS, revised June 2024. Grade 3: '+x['PLAN_META']['sources']['g3']+' Grade 4: '+x['PLAN_META']['sources']['g4'])
save('teks-reference.pdf',story)
for w in x['WEEKS']:
 story=title('Week '+str(w['n'])+' | Teaching map',w['dates']+' | '+w['theme'])
 for j,key in enumerate(keys):
  if j:story.append(PageBreak())
  story.append(p(labels[j],'Heading1'))
  for g in ['g3','g4']:
   story.append(p('Grade '+g[1],'Heading2'));story+=standard_sections(key,w['skills'][key][g]['teks'])
   for l in [a for a in x['LESSONS'] if a['week']==w['n']]:story+=section(l['date'],l['subjects'][j]['targets'][g]['skill'])
  story+=section('Teach and collect evidence','Use the dated lesson sheet for I Do, We Do, You Do and the independent rotation. Record the exact response, correct/total and support separately. Friday checks use the same targets.')
 save('week-'+str(w['n'])+'-plan.pdf',story)
 l=next(a for a in x['LESSONS'] if a['week']==w['n'] and a['friday'])
 story=title('Week '+str(w['n'])+' | Reading and spelling check',l['date']+' | Student __________ Grade ____')
 story+=section('Spelling','Three individually taught words: __________  __________  __________. Record the selected spelling pattern and its confirmed TEKS on the resource selection sheet. Correct / 3: ____ Extra help: ____')
 for g in [3,4]:
  story.append(PageBreak());story+=title('Grade '+str(g)+' | '+l['books']['g'+str(g)]['title'])
  story+=standard_sections('reading',l['subjects'][0]['targets']['g'+str(g)]['codes'])
  for i,q in enumerate(l['books']['q'+str(g)]):story+=section(str(i+1)+'. '+q,'Response / page evidence: __________________________________________\nHelp given: __________________')
  story+=section('Teacher answer key',' | '.join(l['books']['key'+str(g)]))
 save('week-'+str(w['n'])+'-reading-check.pdf',story)
# Printable record pages, with space to use them.
def blank_rows(headers,n,widths,height=44):
 t=table([headers]+[[' ']*len(headers) for _ in range(n)],widths);t._argH=[None]+[height]*n;return t
story=title('Weekly grades and evidence','Student __________ Grade ____ Week ____ Friday __________')
story.append(p('Write the subject and exact TEKS code; attach the dated response or photo. Keep accuracy, planned access and extra prompts separate. Apply confirmed campus grading rules.'))
story.append(table([['Check','TEKS / taught skill','Correct / total','Help / evidence']]+[[a,'\n________________','____ / ____','\n________________'] for a in ['Spelling','Reading','Math','Science / lab','Writing or social studies']],[90,180,90,168]))
story+=section('Response conditions','Planned response mode: __________________  Planned access: __________________\nExtra prompt: I / V / G / M / P / NR. I = independent with planned access; NR = no response.')
story+=section('Next instruction','Reteach / repeat with less help / extend: __________________________________________')
save('weekly-grade-evidence.pdf',story)
story=title('Student progress log','Student __________ Grade ____ Date range __________')
story+=section('Name the target','Subject / TEKS: __________________  Daily learning target: __________________\nActual IEP goal, if applicable: __________________________________________________')
story+=section('Keep conditions consistent','Response method: __________ Planned access: __________ Trials: ____ Measurement unit: __________')
story.append(blank_rows(['Date / task','Correct / total or raw measure','Extra prompt / NR','Evidence / next step'],7,[90,130,105,203]))
story.append(p('Prompt key: I independent with planned access; V verbal; G gesture; M model; P physical; NR no response. NR is not automatically an incorrect academic response. Use an IEP measure only when it matches the actual goal.'))
save('monitoring-log.pdf',story)
story=title('Actual IEP goal setup','No IEP goals are prefilled. Copy the current approved goal before planning formal probes.')
for a in ['Student initials and grade','Exact approved goal wording','Baseline and date','Target criterion and unit of measurement','Required response conditions and access','Probe materials and equivalent examples','Frequency, trial count and reporting dates','How the classroom task matches the goal','Where the evidence will be stored']:
 story+=section(a,'_____________________________________________________________________\n_____________________________________________________________________')
save('iep-setup.pdf',story)
story=title('Progress across nine weeks','Student __________ Actual goal / TEKS __________ Unit __________')
story.append(p('Baseline: ______ Date: ______ Criterion: ______ Planned access: __________________\nKeep raw measures and trial counts visible. Do not compare percentages from different tasks as if they measure the same skill.'))
story.append(blank_rows(['Week / date','Raw measure / trials','Response and help','Next step'],9,[85,130,150,163],40));save('goal-trend.pdf',story)
story=title('Daily routine step record','Student __________ Routine __________ Date __________')
story.append(p('Write observable steps from the actual routine. This is classroom evidence unless the routine and measurement match an approved IEP goal.'))
story.append(blank_rows(['Step to observe','Response','Help / no response','Next practice'],8,[200,100,115,113]));save('task-analysis.pdf',story)
story=title('Choose this week’s licensed lessons','Week ____ Grade 3 learner __________ Grade 4 learner __________')
story.append(p('Start with the calendar’s daily target. Select the matching lesson inside the licensed account; no publisher lesson numbers or student placement are assumed.'))
story.append(table([['Resource and role','Grade 3 lesson / target','Grade 4 lesson / target']]+[[a,'________________\n________________','________________\n________________'] for a in ['HMH: reading and writing','HMH: assessed spelling pattern / exact TEKS','STEMscopes: paced math skill','McGraw Hill: science concept','Bridges: placement-selected intervention','Vizzle: already-taught independent practice']],[188,170,170]))
story+=section('Three taught spelling words per learner','Grade 3: __________  __________  __________\nGrade 4: __________  __________  __________')
save('resource-selector.pdf',story)
story=title('Reading response and story mats','Pair these labels with real book illustrations, objects or the student’s existing symbols.')
story.append(table([['Character / topic','Problem / key idea'],['\n\n\n','\n\n\n'],['Action / important detail','Result / what the detail shows'],['\n\n\n','\n\n\n']],[264,264]))
story+=section('Return to the book','Book __________ Page / scene __________\nMy answer __________ The book shows __________\nTeacher: record the response and help separately. Picture matching alone does not demonstrate a theme or central idea.')
story.append(PageBreak());story+=title('First, next, then','Use for a taught sequence. Add real photos, props or symbols.')
story.append(table([['First','Next','Then'],['\n\n\n\n','\n\n\n\n','\n\n\n\n']],[176]*3))
story+=section('Independent routine','First: familiar task __________  Then: finished basket / planned break __________\nHelp signal __________  Finish after ____ items.');save('response-story-mats.pdf',story)
story=title('Writing and source-evidence frames','Use the actual book, photo, map or history source. A frame supports composition; it is not an answer key.')
for a,b in [('Reading response | 3.7B','In __________, I learned / noticed __________. The page shows __________.'),('Compare sources | 4.7B','Both __________ and __________ show __________. They differ because __________. My evidence is __________.'),('Story message','The topic is __________. The message is __________. The character’s action __________ supports it.'),('History claim | 3.14F','My claim: __________. Source title / creator / date: __________. This detail supports it: __________.'),('Texas history','Person / event: __________. What happened: __________. A cause or effect: __________. Source evidence: __________.'),('Teacher record','Response method: __________. Planned access: __________. Extra prompt: __________. Next step: __________.')]:story+=section(a,b)+[Spacer(1,16)]
save('writing-history-frames.pdf',story)
story=title('Equal groups and sharing mat','Math: 3.4D, 3.4E, 3.4H, 3.4J; supported division models for 4.4E.')
story.append(p('Make equal groups to multiply, or share the total equally to divide. Tell whether the unknown is the number of groups or the number in each group.'))
story.append(table([['Group 1','Group 2','Group 3'],['\n\n\n\n\n','\n\n\n\n\n','\n\n\n\n\n']],[176]*3))
story+=section('Connect model and equation','____ groups of ____ = ____ total.\n____ divided by ____ = ____.\nRelated multiplication fact: __________________')
story+=section('Fresh response','New total / groups: __________  Student response: __________  Extra help: __________');save('sharing-mat.pdf',story)
from reportlab.platypus import Flowable
class Strips(Flowable):
 def __init__(self):Flowable.__init__(self);self.width=528;self.height=330
 def draw(self):
  c=self.canv
  for row,n in enumerate([1,2,3,4,6,8]):
   y=300-row*52;c.setFont('Helvetica',10);c.drawString(0,y+13,'Whole' if n==1 else f'{n} equal parts')
   for i in range(n):c.rect(95+i*432/n,y,432/n,32);c.drawCentredString(95+(i+.5)*432/n,y+12,'1' if n==1 else f'1/{n}')
story=title('Equal-length fraction strips','Math: 3.3A/C/D/F/G/H and 4.3A/B/C/D/E')+[p('Each row is the same-size whole. Print at actual size. Cut individual parts only after comparing equal whole lengths.'),Strips()]
story+=section('Build, compare, explain','Build 3/4 from unit fractions. Compare 1/2 with 2/4, then 1/2 with 3/4. Record an equation or comparison and show why it is true.');save('fraction-strips.pdf',story)
class Grid(Flowable):
 def __init__(self):Flowable.__init__(self);self.width=528;self.height=320
 def draw(self):
  c=self.canv
  for r in range(8):
   for col in range(12):c.rect(48+col*36,20+r*36,36,36)
story=title('Array, area and perimeter mat','Math: 3.4D/E; 4.5C/D')+[p('Use each square as one square unit. Outline a 2-by-3 rectangle. Count tiles inside for area and unit edges around it for perimeter.'),Grid()]
story+=section('Connect the formulas','Area: ____ rows × ____ columns = ____ square units.\nPerimeter: ____ + ____ + ____ + ____ = ____ units.\nExplain how your model supports the formula: __________________');save('array-mat.pdf',story)
story=title('Science investigation record','Student __________ Date __________ TEKS __________')
for a,b in [('Our question','What will we test? __________________'),('Plan and predict','I think __________ because __________.\nWhat stays the same? __________ What changes? __________'),('Observe three trials','Trial 1: __________ Trial 2: __________ Trial 3: __________'),('Explain with evidence','I observed __________. This supports __________ because __________.'),('Energy investigation','Same car and block; slow/faster runs. Record observed speed and effect on the block. Reset and repeat.'),('Mixture investigation','Mass before: ____ Mass after: ____ Same closed container, no spills. What do these readings show?'),('Teacher evidence','Correct / total: ____ Extra prompts: ____ Response method: ____ Next step: ____')]:story+=section(a,b)+[Spacer(1,14)]
save('science-record.pdf',story)
# Replace the interrupted aggregate packets with these current component files.
from pypdf import PdfWriter
def merge(name,files):
 writer=PdfWriter()
 for f in files:writer.append(str(P/f),outline_item=f.removesuffix('.pdf').replace('-',' '))
 writer.write(str(P/name));writer.close()
merge('full-binder.pdf',['routine.pdf','teks-reference.pdf']+[f'week-{w["n"]}-plan.pdf' for w in x['WEEKS']]+[f'day-{l["date"]}.pdf' for l in x['LESSONS']]+['parent-outlines.pdf'])
merge('full-assessments.pdf',[f'week-{w["n"]}-friday.pdf' for w in x['WEEKS']]+['weekly-grade-evidence.pdf','iep-setup.pdf','monitoring-log.pdf','goal-trend.pdf','task-analysis.pdf'])
import subprocess,sys
subprocess.run([sys.executable,str(ROOT/'scripts/make_student_printables.py')],check=True)
merge('full-resources.pdf',['book-shopping-list.pdf','seasonal-guide.pdf']+[f'week-{w["n"]}-book-guide.pdf' for w in x['WEEKS']]+[f'week-{w["n"]}-student-printables.pdf' for w in x['WEEKS']]+['response-story-mats.pdf','writing-history-frames.pdf','sharing-mat.pdf','fraction-strips.pdf','array-mat.pdf','science-record.pdf','resource-selector.pdf','parent-outlines.pdf'])
print('Completed every original PDF and the missing TEKS reference:',len(list(P.glob('*.pdf'))),'PDFs.')
