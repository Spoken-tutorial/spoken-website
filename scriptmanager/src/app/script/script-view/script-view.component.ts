import { Component, OnInit, Input, ElementRef, Renderer2, ViewChild } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { CreateScriptService } from '../../_service/create-script.service';
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
  @Input() nav: any;
  @ViewChild('tableRow') el: ElementRef;
  @ViewChild('newmodal') el2: ElementRef;

  constructor(
    private route: ActivatedRoute,
    public createscriptService: CreateScriptService,
    public revisionsService: RevisionsService,
    private rd: Renderer2
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

  public getComment() {
    this.createscriptService.getComment(
      this.slideId
    ).subscribe(
      (res) => {
        this.comments = res;
      },
    );
  }

  public postComment(comment) {
    this.createscriptService.postComment(
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
      this.comment = true;
      this.el.nativeElement.querySelectorAll('tr')[i + 1].classList.add('is-selected')
    }
    else {
      if (this.comment == false) {
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
    // console.log(this.revisions[this.index2]['date_time'])
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
        this.revisions.shift();
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
      this.revision = true;
    }
    else {
      if (this.revision == false) {
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
