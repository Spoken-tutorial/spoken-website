import { Component, OnInit, Input, ElementRef, Renderer2, ViewChild } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { CreateScriptService } from '../../_service/create-script.service';

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
  public comments: any = [];
  public tutorialName: any;
  public slideId: number;
  public index: number = 0;
  @Input() nav: any;
  @ViewChild('tableRow') el: ElementRef;

  constructor(
    private route: ActivatedRoute,
    public createscriptService: CreateScriptService,
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

  ngOnInit() {
    this.route.params.subscribe(params => {
      this.id = +params['id'];
    });
    this.viewScript();
    this.tutorialName = this.route.snapshot.params['tutorialName']
  }

}
