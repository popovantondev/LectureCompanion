"""Regression checks for documentation metadata; never starts the application."""
import copy, importlib.util, json, tempfile, unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('public_docs',Path(__file__).with_name('check_public_docs.py'))
docs=importlib.util.module_from_spec(spec);spec.loader.exec_module(docs)
class PublicDocsTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.previous=docs.ROOT;docs.ROOT=Path(self.temp.name)
        self.data={'repo':'Example','name':'Example','version':'1.0','platform':'macOS','tag':None,'status':'source','release_url':None,'source_url':'https://github.com/popovantondev/Example','help_url':'https://popovantondev.github.io/Example/Guide-{lang}.html','feedback_url':'https://github.com/popovantondev/Example/issues/new/choose','downloads':[],'assets':[],'checksums':[],'description':dict.fromkeys(docs.LANGS,'An application.'),'requirements':dict.fromkeys(docs.LANGS,'Source setup.'),'start':dict.fromkeys(docs.LANGS,'Read the guide.'),'version_files':[{'path':'VERSION','pattern':r'^(\S+)$'}]}
        (docs.ROOT/'VERSION').write_text('1.0')
        self.files={'README.md':docs.markdown(self.data,'en')}
        (docs.ROOT/'README.md').write_text(self.files['README.md'],encoding='utf-8')
    def tearDown(self):docs.ROOT=self.previous;self.temp.cleanup()
    def check(self):return docs.validate(self.data,self.files)
    def test_valid_metadata(self):self.assertEqual(self.check(),[])
    def test_summary_drift(self):
        (docs.ROOT/'README.md').write_text('changed');self.assertTrue(any('regenerate' in e for e in self.check()))
    def test_version_drift(self):
        (docs.ROOT/'VERSION').write_text('2.0');self.assertTrue(any('version mismatch' in e for e in self.check()))
    def test_raw_html_destination(self):
        self.data['help_url']='https://github.com/popovantondev/Example/blob/main/Guide-{lang}.html';self.assertTrue(any('published HTML' in e for e in self.check()))
    def test_source_only_download(self):
        self.data['downloads']=['app.zip'];self.assertTrue(any('source-only' in e for e in self.check()))
    def test_missing_image(self):
        (docs.ROOT/'README.md').write_text(self.files['README.md']+'\n![Example](missing.png)');self.assertTrue(any('missing image' in e for e in self.check()))
    def test_missing_local_document(self):
        (docs.ROOT/'README.md').write_text(self.files['README.md']+'\n[Setup](missing.md)');self.assertTrue(any('missing local link' in e for e in self.check()))
    def test_production_credit(self):
        (docs.ROOT/'README.md').write_text(self.files['README.md']+'\nCreated with ChatGPT');self.assertTrue(any('production content' in e for e in self.check()))
    def test_functional_codex_reference_allowed(self):
        text=self.files['README.md']+'\nRuns approved tasks through Codex.';self.files['README.md']=text;(docs.ROOT/'README.md').write_text(text);self.assertEqual(self.check(),[])
    def test_internal_instruction_file(self):
        (docs.ROOT/'AGENTS.md').write_text('Internal notes');self.assertTrue(any('Internal document' in e for e in self.check()))
    def test_missing_translation(self):
        del self.data['description']['ru'];self.assertTrue(any('incomplete localization' in e for e in self.check()))
    def test_release_tag_destination(self):
        self.data.update(tag='v1.0',release_url='https://github.com/popovantondev/Example/releases/latest',status='release');self.assertTrue(any('URL/tag mismatch' in e for e in self.check()))
    def test_guides_link_to_landing(self):
        root=Path(__file__).resolve().parents[1];labels={'ru':'← На страницу программы','de':'← Zur Programmseite','en':'← Program page'};pages={'de':'index.html','en':'index-en.html','ru':'index-ru.html'};found=0
        for folder in (root,root/'docs',root/'website'):
            for lang in labels:
                guide=folder/f'Guide-{lang}.html'
                if not guide.is_file():continue
                html=guide.read_text(encoding='utf-8')
                if 'http-equiv="refresh"' in html:continue
                found+=1
                self.assertRegex(html,r'<a\b[^>]*href="'+pages[lang]+r'"[^>]*>\s*'+labels[lang]+r'\s*</a>',str(guide))
                self.assertTrue((folder/pages[lang]).is_file(),str(folder/pages[lang]))
        self.assertGreaterEqual(found,3)
    def test_guides_have_live_robot_scene_and_no_empty_block(self):
        root=Path(__file__).resolve().parents[1];found=0
        for lang in ('ru','de','en'):
            html=(root/f'Guide-{lang}.html').read_text(encoding='utf-8')
            if 'http-equiv="refresh"' in html:continue
            found+=1
            self.assertRegex(html,r'<figure class="robot-preview robot-wide">\s*<div class="robot-stage robot-dock"[^>]*data-robot-mode="dock"[^>]*>',lang)
            self.assertIn('<article class="robot-demo-card',html,lang)
            self.assertNotIn('guide-screenshot"',html.split('</style>')[-1],lang)
            self.assertNotRegex(html,r'<section class="overview">\s*</section>',lang)
        self.assertEqual(found,3)
class RobotTemplateTests(unittest.TestCase):
    """The robot answers common questions offline: every phrase below must hit a topic (not 'I don't know'); small talk keeps working."""
    SCRIPT="""var fs=require('fs');var src=fs.readFileSync(process.argv[1],'utf8');
var code=src.slice(src.indexOf('  var TOPICS = ['),src.indexOf('  var unlocked'));
var Q=JSON.parse(process.argv[2]);var out=[];
['ru','de','en'].forEach(function(LANG){var f=new Function('LANG',code+';return findTopic;')(LANG);
Q[LANG].forEach(function(q){out.push([LANG,q[0],f(q[0])?1:0,q[1]])})});console.log(JSON.stringify(out));"""
    def test_common_questions_get_a_template_answer(self):
        import os, shutil, subprocess
        node=os.environ.get('NODE') or shutil.which('node') or r'C:\Users\Public\CLODE\tools\node\node.exe'
        if not Path(node).exists() and not shutil.which(node):self.skipTest('node not found')
        robot=os.environ.get('ROBOT_JS') or str(Path(__file__).resolve().parents[1]/'assets'/'robot.js')
        topics={'ru':['Работает ли без интернета?','Защита данных','Какие данные отправляются?','Сколько стоит?','Это бесплатно?','Какие языки поддерживает?','Какие системные требования?','Сколько нужно места на диске','Нужна ли видеокарта?','Как установить?','Безопасно ли? Это не вирус?','Для чего это нужно?','Где руководство?','Не работает, что делать?','Работает ли без интрнета?'],
          'de':['Funktioniert es ohne Internet?','Datenschutz','Welche Daten werden gesendet?','Was kostet das?','Ist das kostenlos','Welche Sprachen gibt es?','Welche Systemanforderungen gibt es?','wie viel Speicherplatz brauche ich','Brauche ich eine Grafikkarte?','Wie installiere ich es?','Ist das sicher? Kein Virus?','Wofür ist das gut','Wo ist die Anleitung?','Es funktioniert nicht, was tun?','Funktioniert es ohne Internte?'],
          'en':['Does it work without internet?','Data protection','What data is sent?','How much does it cost?','Is it free?','Which languages are supported?','What are the system requirements?','how much disk space do I need','Do I need a graphics card?','How do I install it?','Is it safe? Not a virus?','What is it for?','Where is the guide?','It is not working, what now?','Does it work without interent?']}
        smalltalk={'ru':['Привет','Как дела?'],'de':['Hallo','Wie geht es dir?'],'en':['Hi','How are you?']}
        silly={'ru':'расскажи анекдот про кота','de':'wie wird das Wetter morgen','en':'tell me a joke about cats'}
        data={l:[[q,'topic'] for q in topics[l]+smalltalk[l]]+[[silly[l],'none']] for l in topics}
        run=subprocess.run([node,'-e',self.SCRIPT,robot,json.dumps(data,ensure_ascii=False)],capture_output=True,encoding='utf-8')
        self.assertEqual(run.returncode,0,run.stderr)
        for lang,question,hit,kind in json.loads(run.stdout):
            self.assertEqual(bool(hit),kind=='topic',lang+': '+question)
class NetworkRetryTests(unittest.TestCase):
    def test_transient_connection_error_is_retried(self):
        import io
        from unittest.mock import patch
        with patch.object(docs.urllib.request, 'urlopen', side_effect=[ConnectionResetError('reset'), io.BytesIO(b'ok')]) as request, patch.object(docs.time, 'sleep'):
            self.assertEqual(docs.fetch_bytes('https://example.invalid'), b'ok')
            self.assertEqual(request.call_count, 2)

    def test_not_found_is_not_retried(self):
        from unittest.mock import patch
        error=docs.urllib.error.HTTPError('https://example.invalid', 404, 'Not found', {}, None)
        with patch.object(docs.urllib.request, 'urlopen', side_effect=error) as request, patch.object(docs.time, 'sleep'):
            with self.assertRaises(docs.urllib.error.HTTPError):
                docs.fetch_bytes('https://example.invalid')
            self.assertEqual(request.call_count, 1)

    def test_temporary_server_error_is_retried(self):
        import io
        from unittest.mock import patch
        error=docs.urllib.error.HTTPError('https://example.invalid', 503, 'Unavailable', {}, None)
        with patch.object(docs.urllib.request, 'urlopen', side_effect=[error, io.BytesIO(b'ok')]), patch.object(docs.time, 'sleep'):
            self.assertEqual(docs.fetch_bytes('https://example.invalid'), b'ok')

    def test_persistent_connection_error_still_fails(self):
        from unittest.mock import patch
        with patch.object(docs.urllib.request, 'urlopen', side_effect=ConnectionResetError('reset')) as request, patch.object(docs.time, 'sleep'):
            with self.assertRaises(ConnectionResetError):
                docs.fetch_bytes('https://example.invalid')
            self.assertEqual(request.call_count, 3)

if __name__=='__main__':unittest.main()
