import { Component, OnInit, Input } from '@angular/core';
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
  @Input() nav: any;

  constructor(
    private route: ActivatedRoute,
    public createscriptService: CreateScriptService
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
    ).subscribe(
      console.log,
      console.error
    );
    this.getComment();
  }

  public viewComment(i) {
    this.slideId = this.slides[i]['id'];
    this.getComment();
    this.comment = true;
  }

  ngOnInit() {
    this.route.params.subscribe(params => {
      this.id = +params['id'];
    });
    this.viewScript();
    this.tutorialName = this.route.snapshot.params['tutorialName']
  }

}
