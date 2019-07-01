import { Component, OnInit, Input, ElementRef, Renderer2, ViewChild } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { CreateScriptService } from '../../_service/create-script.service';
import { CommentsService } from '../../_service/comments.service';
import { RevisionsService } from '../../_service/revisions.service';

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
  public overVal:boolean[]=[false];
  @Input() nav: any;
  @ViewChild('tableRow') el: ElementRef;
  @ViewChild('newmodal') el2: ElementRef;
  public mystyle={
    // display:hidden,
  }
  constructor(
    private route: ActivatedRoute,
    public createscriptService: CreateScriptService,
    public commentsService: CommentsService,
    public revisionsService: RevisionsService,
    private rd: Renderer2
  ) { }
  public mouseenter(i){
    this.overVal[i]=true;
  }
  public mouseleave(i){
    this.overVal[i]=false;
  }

  public viewScript() {
    this.createscriptService.getScript(
      this.id
    ).subscribe(
      (res) => {
        this.slides = res;
      },
    );
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

  public viewModal(index) {
    this.index2 = index
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
        if (this.revisions.length == 0) {
          this.revisions = false;
        }
      },
    );
  }

  public viewRevision(i) {
    if (this.slideIdRev != i) {
      this.slideIdRev = i
      this.getRevison(i);
      if (this.comment == true) {
        this.comment = false;
      }
      this.revision = true;
    }
    else {
      if (this.revision == false) {
        if (this.comment == true) {
          this.comment = false;
        }
        this.revision = true;
      }
      else {
        this.revision = false;
      }
    }
  }

  ngOnInit() {
    this.route.params.subscribe(params => {
      this.id = +params['id'];
    });
    this.viewScript();
    this.tutorialName = this.route.snapshot.params['tutorialName']
  }

}
