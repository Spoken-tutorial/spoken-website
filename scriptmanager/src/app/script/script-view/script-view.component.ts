import { Component, OnInit, Input, ElementRef, Renderer2, ViewChild } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { CreateScriptService } from '../../_service/create-script.service';
import { CommentsService } from '../../_service/comments.service';
import { RevisionsService } from '../../_service/revisions.service';
import { Observable, Subject } from 'rxjs';
import * as $ from 'jquery';

export interface DiffContent {
  leftContent: string;
  rightContent: string;
}

@Component({
  selector: 'app-script-view',
  templateUrl: './script-view.component.html',
  styleUrls: ['./script-view.component.sass']
})

export class ScriptViewComponent implements OnInit {
  public slides: any = [];
  public tutorials: any = [];
  private id: number;
  public comment = false;
  public revision = false;
  public comments: any = [];
  public revisions: any;
  public tutorialName: any;
  public slideId: number;
  public slideIdRev: number;
  public index: number = 0;
  public index2: number = 0;
  public overVal: boolean[] = [false];
  public revision_old;
  public revision_new;

  submitted = false;
  content: DiffContent = {
    leftContent: '',
    rightContent: ''
  };
  options: any = {
    lineNumbers: true,
    mode: 'xml'
  };

  contentObservable: Subject<DiffContent> = new Subject<DiffContent>();
  contentObservable$: Observable<DiffContent> = this.contentObservable.asObservable();

  @Input() nav: any;
  @ViewChild('tableRow') el: ElementRef;
  @ViewChild('newmodal') el2: ElementRef;

  constructor(
    private route: ActivatedRoute,
    public createscriptService: CreateScriptService,
    public commentsService: CommentsService,
    public revisionsService: RevisionsService,
    public router: Router
  ) { }

  public viewScript() {
    this.createscriptService.getScript(
      this.id
    ).subscribe(
      (res) => {
        this.slides = res;
      },
    );
  }

  public mouseenter(i) {
    this.overVal[i] = true;
  }

  public mouseleave(i) {
    this.overVal[i] = false;
  }

  public getComment() {
    this.commentsService.getComment(
      this.slideId
    ).subscribe(
      (res) => {
        this.comments = res;
      },
    );
  }

  public postComment(comment) {
    this.commentsService.postComment(
      this.slideId,
      {
        "comment": comment
      }
    ).subscribe();
    this.getComment();
    this.getComment();
  }

  public viewComment(i) {
    this.el.nativeElement.querySelectorAll('tr')[this.index + 1].classList.remove('is-selected')
    this.index = i
    if (this.slideId != this.slides[i]['id']) {
      this.slideId = this.slides[i]['id']
      this.getComment();
      if (this.revision == true) {
        this.revision = false;
      }
      this.comment = true;
      this.el.nativeElement.querySelectorAll('tr')[i + 1].classList.add('is-selected')
    }
    else {
      if (this.comment == false) {
        if (this.revision == true) {
          this.revision = false;
        }
        this.comment = true;
        this.el.nativeElement.querySelectorAll('tr')[i + 1].classList.add('is-selected')
      }
      else {
        this.comment = false;
        this.el.nativeElement.querySelectorAll('tr')[i + 1].classList.remove('is-selected')
      }
    }
  }

  public console(data) {
    console.log(data);
    return data;
  }

  public viewModal(index) {
    this.index2 = index;

    // const text1 = $.trim($(this.revisions[index + 1]['cue']).text());
    // const text2 = $.trim($(this.revisions[index]['cue']).text());

    // this.content.leftContent = text1;
    // this.content.rightContent = text2;
    // this.submitComparison();

    this.el2.nativeElement.classList.add('is-active')
  }

  public hideModal() {
    this.el2.nativeElement.classList.remove('is-active')
  }

  public getRevison(i) {
    this.revisionsService.getRevisions(
      i
    ).subscribe(
      (res) => {
        this.revisions = res;
        this.revision_new = res;
        if (this.revisions.length == 0) {
          this.revisions = false;
        }
      },
    );
  }

  public viewRevision(i, slidePK) {
    this.el.nativeElement.querySelectorAll('tr')[this.index + 1].classList.remove('is-selected');
    this.index = i
    if (this.slideIdRev != slidePK) {
      this.slideIdRev = slidePK
      this.getRevison(slidePK);
      if (this.comment == true) {
        this.comment = false;
      }
      this.revision = true;
      this.el.nativeElement.querySelectorAll('tr')[i + 1].classList.add('is-selected')
    }
    else {
      if (this.revision == false) {
        if (this.comment == true) {
          this.comment = false;
        }
        this.revision = true;
        this.el.nativeElement.querySelectorAll('tr')[i + 1].classList.add('is-selected')
      }
      else {
        this.revision = false;
        this.el.nativeElement.querySelectorAll('tr')[i + 1].classList.remove('is-selected')
      }
    }
  }

  public revert(reversionData) {
    this.revisionsService.revertRevision(
      reversionData['id'],
      {
        "reversion_id": reversionData['reversion_id']
      }
    ).subscribe();

    window.location.reload();
  }

  ngOnInit() {
    this.route.params.subscribe(params => {
      this.id = +params['id'];
    });
    this.viewScript();
    this.tutorialName = this.route.snapshot.params['tutorialName'];
  }

  //diff on revisions
  public submitComparison() {
    this.submitted = false;
    this.contentObservable.next(this.content);
    this.submitted = true;
  }

  public handleChange(side: 'left' | 'right', value: string) {
    // console.log(side);
    switch (side) {
      case 'left':
        this.content.leftContent = 'value';
        break;
      case 'right':
        this.content.rightContent = value;
        break;
      default:
        break;
    }
  }

}
