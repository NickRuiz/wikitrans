from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import iri_to_uri
from django.conf import settings
from django.contrib.auth.models import User

from wt_languages.models import LANGUAGE_CHOICES
from wt_languages.models import TARGET_LANGUAGE,SOURCE_LANGUAGE,BOTH
from wt_languages.models import LanguageCompetancy
from wt_articles import TRANSLATORS
from wt_articles.splitting import determine_splitter

from BeautifulSoup import BeautifulSoup
from datetime import datetime

# Generic relation to mturk_manager
from django.contrib.contenttypes import generic
from mturk_manager.models import TaskItem, HITItem, AssignmentItem
from urllib import quote_plus, unquote_plus

from urllib import quote_plus, unquote_plus

import re

if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
else:
    notification = None

class ArticleOfInterest(models.Model):
    title = models.CharField(_('Title'), max_length=255)
    title_language = models.CharField(_('Title language'),
                                      max_length=2,
                                      choices=LANGUAGE_CHOICES)
    target_language = models.CharField(_('Target language'),
                                       max_length=2,
                                       choices=LANGUAGE_CHOICES)

    def __unicode__(self):
        return u"%s :: %s" % (self.title, self.target_language)

class SourceArticle(models.Model):
    title = models.CharField(_('Title'), max_length=255)
    language = models.CharField(_('Source Language'),
                                max_length=2,
                                choices=LANGUAGE_CHOICES)
    #version = models.IntegerField(_('Version')) # @@@ try django-versioning
    timestamp = models.DateTimeField(_('Import Date'), default=datetime.now())
    doc_id = models.CharField(_('Document ID'), max_length=512)
    source_text = models.TextField(_('Source Text'))
    sentences_processed = models.BooleanField(_('Sentences Processed'))

    # hook into mturk manager
    #hits = generic.GenericRelation(HITItem)
    hits = generic.GenericRelation(TaskItem)

    def __unicode__(self):
        return u"%s :: %s :: %s" % (self.id, self.doc_id, self.title)

    def save(self, manually_splitting=False, source_sentences=()):       
        if not manually_splitting:
            # Tokenize the HTML that is fetched from a wiki article
            sentences = list()
            segment_id = 0
            soup = BeautifulSoup(self.source_text)
            sentence_splitter = determine_splitter(self.language)
            # initial save for foreign key based saves to work
            # save should occur after sent_detector is loaded
            super(SourceArticle, self).save()
            # find all paragraphs
            for p in soup.findAll('p'):
                only_p = p.findAll(text=True)
                p_text = ''.join(only_p)
                # split all sentences in the paragraph
                
                sentences = sentence_splitter(p_text.strip())
                # TODO: remove bad sentences that were missed above
                sentences = [s for s in sentences if not re.match("^\**\[\d+\]\**$", s)]
                    
                for sentence in sentences:
                    # Clean up bad spaces (&#160;)
                    sentence = sentence.replace("&#160;", " ")
                    
                    s = SourceSentence(article=self, text=sentence, segment_id=segment_id)
                    segment_id += 1
                    s.save()
                s.end_of_paragraph = True
                s.save()
            self.sentences_processed = True
        else:
            for sentence in source_sentences:
                sentence.save()
        super(SourceArticle, self).save()
        
    def delete_sentences(self):
        for sentence in self.sourcesentence_set.all():
            SourceSentence.delete(sentence)
    
    def get_absolute_url(self):
        url = '/articles/source/%s/%s/%s' % (self.language,
                                             quote_plus(self.title.encode('utf-8')),
                                             self.id)
        return iri_to_uri(url)

    def get_relative_url(self, lang_string=None):
        if lang_string == None:
            lang_string = self.language
        url = '%s/%s/%s' % (lang_string,
                            quote_plus(self.title.encode('utf-8')),
                            self.id)
        return iri_to_uri(url)
    
    def sentences_to_lines(self):
        lines = []
        for sentence in self.sourcesentence_set.order_by('segment_id'):
            text = sentence.text
            if sentence.end_of_paragraph:
                text += "\n"
            lines.append(text)
                
        return "\n".join(lines).strip()
    def lines_to_sentences(self, lines):
        segment_id = 0
        source_sentences = []
        
        # Get each sentence; mark the last sentence of each paragraph
        sentences = lines.split("\n")
        s_count = len(sentences)
        for i in range(0, s_count):
            if i > 0 and len(sentences[i].strip()) == 0:
                source_sentences[segment_id-1].end_of_paragraph = True
            else:
                s = SourceSentence(article=self, text=sentences[i], segment_id=segment_id)
                
                source_sentences.append(s)
                segment_id += 1
                
        return source_sentences

class SourceSentence(models.Model):
    article = models.ForeignKey(SourceArticle)
    text = models.CharField(_('Sentence Text'), max_length=2048)
    segment_id = models.IntegerField(_('Segment ID'))
    end_of_paragraph = models.BooleanField(_('Paragraph closer'))

    class Meta:
        ordering = ('segment_id','article')

    def __unicode__(self):
        return u"%s :: %s :: %s" % (self.id, self.segment_id, self.text)
    
    def save(self):
        super(SourceSentence, self).save()

class TranslationRequest(models.Model):
    article = models.ForeignKey(SourceArticle)
    target_language = models.CharField(_('Target Language'),
                                       max_length=2,
                                       choices=LANGUAGE_CHOICES)
    date = models.DateTimeField(_('Request Date'))
    translator = models.CharField(_('Translator type'),
                                  max_length=512,
                                  choices=TRANSLATORS)

    def __unicode__(self):
        return u"%s: %s" % (self.target_language, self.article)

class TranslatedSentence(models.Model):
    segment_id = models.IntegerField(_('Segment ID'))
    source_sentence = models.ForeignKey(SourceSentence)
    text = models.CharField(_('Translated Text'), blank=True, max_length=2048)
    translated_by = models.CharField(_('Translated by'), blank=True, max_length=255)
    language = models.CharField(_('Language'), blank=True, max_length=2)
    translation_date = models.DateTimeField(_('Import Date'))
    approved = models.BooleanField(_('Approved'), default=False)
    end_of_paragraph = models.BooleanField(_('Paragraph closer'))

    class Meta:
        ordering = ('segment_id',)

    def __unicode__(self):
        return u'%s' % (self.id)

class TranslatedArticle(models.Model):
    article = models.ForeignKey(SourceArticle)
    parent = models.ForeignKey('self', blank=True, null=True, related_name='parent_set')
    title = models.CharField(_('Title'), max_length=255)
    timestamp = models.DateTimeField(_('Timestamp'))
    language = models.CharField(_('Language'),
                                max_length=2,
                                choices=LANGUAGE_CHOICES)
    sentences = models.ManyToManyField(TranslatedSentence)
    approved = models.BooleanField(_('Approved'), default=False)

    def set_sentences(self, translated_sentences):
        source_sentences = self.article.sourcesentence_set.order_by('segment_id')
        source_segment_ids = [s.segment_id for s in source_sentences]
        translated_segment_ids = [s.segment_id for s in translated_sentences]
        if len(source_segment_ids) != len(translated_segment_ids):
            raise ValueException('Number of translated sentences doesn\'t match number of source sentences')
        if source_segment_ids != translated_segment_ids:
            ValueException('Segment id lists do not match')
        translated_article_list = [ts.source_sentence.article for ts in translated_sentences]
        if len(translated_article_list) != 1 and translated_article_list[0] != self.article:
            raise ValueException('Not all translated sentences derive from the source article')
        for ts in translated_sentences:
            self.sentences.add(ts)

    def __unicode__(self):
        return u'%s :: %s' % (self.title, self.article)

    #@models.permalink
    def get_absolute_url(self):
        source_lang = self.article.language
        target_lang = self.language
        lang_pair = "%s-%s" % (source_lang, target_lang)
        url = '/articles/translated/%s/%s/%s' % (lang_pair,
                                                 quote_plus(self.title.encode('utf-8')),
                                                 self.id)
        return iri_to_uri(url)

    def get_relative_url(self):
        source_lang = self.article.language
        target_lang = self.language
        lang_pair = "%s-%s" % (source_lang, target_lang)
        url = '%s/%s/%s' % (lang_pair,
                            quote_plus(self.title.encode('utf-8')),
                            self.id)
        return iri_to_uri(url)
    

class FeaturedTranslation(models.Model):
    featured_date = models.DateTimeField(_('Featured Date'))
    article = models.ForeignKey(TranslatedArticle)

    class Meta:
        ordering = ('-featured_date',)

    def __unicode__(self):
        return u'%s :: %s' % (self.featured_date, self.article.title)

def latest_featured_article():
    ft = FeaturedTranslation.objects.all()[0:]
    if len(ft) > 0:
        return ft[0]
    else:
        return None
    
class MTurkTranslatedSentence(TranslatedSentence):
    assignment = models.ForeignKey(AssignmentItem)

    class Meta:
        ordering = ('-segment_id',)

    def __unicode__(self):
        return u'%s' % (self.id)

