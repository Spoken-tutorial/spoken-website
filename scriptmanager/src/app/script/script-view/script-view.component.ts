import { Component, OnInit,Input, Output, EventEmitter } from '@angular/core';
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
  @Input() nav: any;
  public comments: any = [];
  @Output() getCommentEmitter2 = new EventEmitter<any>();

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
  
  public getComment(index) {
    this.comments = [
      {
        "slideId": index,
        "user": "Reviewer 1", 
        "comment": "This comment is from reviewer 1"
      },
      {
        "slideId": index,
        "user": "Reviewer 2", 
        "comment": "This comment is from reviewer 2"
      },
      {
        "slideId": index,
        "user": "Reviewer 3", 
        "comment": "This comment is from reviewer 3"
      },
      {
        "slideId": index,
        "user": "Reviewer 4", 
        "comment": "This comment is from reviewer 4"
      }
    ];
    // this.comments.push(index)
    console.log(this.comments)
  }

  ngOnInit() {
    this.route.params.subscribe(params => {
      this.id = +params['id'];
    });
    this.viewScript();
  }

}
