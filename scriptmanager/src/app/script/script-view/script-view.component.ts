import { Component, OnInit, Input, Output, EventEmitter } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { CreateScriptService } from '../../_service/create-script.service';

@Component({
  selector: 'app-script-view',
  templateUrl: './script-view.component.html',
  styleUrls: ['./script-view.component.sass']
})

export class ScriptViewComponent implements OnInit {
  public slides: any = [];
  private id: number;
  public foss;
  public comment = false;
  @Input() nav: any;
  public comments: any = [];

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

  public onShowComment(val: any) {
    // console.log(val);
    this.getComment();
    this.comment = true;
  }

  public getComment() {
    this.comments = [
      {
        "slideId": 1,
        "user": "Reviewer 1",
        "comment": "This comment is from reviewer 1"
      },
      {
        "slideId": 2,
        "user": "Reviewer 2",
        "comment": "This comment is from reviewer 2"
      },
      {
        "slideId": 1,
        "user": "Reviewer 3",
        "comment": "This comment is from reviewer 3"
      },
      {
        "slideId": 4,
        "user": "Reviewer 4",
        "comment": "This comment is from reviewer 4"
      }
    ];

  }

  ngOnInit() {
    this.route.params.subscribe(params => {
      this.id = +params['id'];
    });
    this.viewScript();
  }

}
